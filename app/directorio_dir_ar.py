"""Crawler directo de la red dir.ar — 13 directorios reales (logística,
limpieza, administración de consorcios, catering, gimnasios, tiendas de ropa,
salud y belleza, seguridad del hogar, talleres mecánicos, gráficas e
imprentas, abogados, transporte), cada uno organizado por ciudad con
dirección y a veces teléfono verificado por el propio sitio.

100% GRATIS — no pasa por Serper, no gasta nada del presupuesto de por
vida. Reemplaza el "site:dominio.dir.ar" en Serper (que sí cuesta) por una
lectura directa de la página de listado, que trae 20-60 empresas de una
sola request. Mismo espíritu que Overpass: fuente gratuita indexada
directamente, con directorio_progress para no re-leer la misma página cada
hora para siempre (el contenido de un directorio no cambia tan rápido).

Generalización de app/directorio_logistica.py (que solo cubría logística,
con categorías conocidas de antemano: "Logística", "Transporte de carga",
etc.). Acá NO se conocen las categorías reales de rubros como tiendas de
ropa o gimnasios, así que el parser ancla únicamente en la línea de rating
(★ X,X (N)), que es universal en toda la red — la línea de categoría, si
existe, se toma como la que está 2 líneas antes del rating (nombre y
dirección son las 2 inmediatamente anteriores).

Varios slugs de subdominio se adivinaron por patrón y no se pudieron
verificar contra el HTML real (WebFetch a dir.ar bloqueado en el entorno de
desarrollo) — si un dominio no devuelve cards nunca, revisar con
`main.py auditar-directorios` y docs/PROMPT_AUDITORIA_DIRECTORIOS.md.
"""
import re

import requests

from app.db import get_conn, now
from app.discovery import _parece_empresa, _ya_existe_en_db, _ya_descubierta, _quitar_acentos
from app.exclusions import es_cadena_excluida, es_zona_prohibida

USER_AGENT = "MotorDeJackpots/1.0 (uso personal, busqueda de empleo)"
TIMEOUT = 15

# dominio -> rubro más probable de sus candidatas (pista para promote.py,
# igual que se hace con el tag de OSM en overpass_discovery.py)
DOMINIOS = {
    "logistica.dir.ar": "logistica",
    "limpieza.dir.ar": "limpieza",
    "administraciondeconsorcios.dir.ar": "administrativo",
    "catering.dir.ar": "atencion_cliente",
    "gimnasios.dir.ar": "atencion_cliente",
    "tiendasderopa.dir.ar": "atencion_cliente",
    "saludybelleza.dir.ar": "atencion_cliente",
    "seguridaddelhogar.dir.ar": "atencion_cliente",
    "talleresmecanicos.dir.ar": "administrativo",
    "graficaseimprentas.dir.ar": "administrativo",
    "abogados.dir.ar": "administrativo",
    "transporte.dir.ar": "logistica",
}

TAG_RE = re.compile(r"<[^>]+>")
RATING_RE = re.compile(r"^★\s*([\d,\.]+)\s*\((\d+)\)$")


def _slug_de_zona(zona: str) -> str:
    return _quitar_acentos(zona.strip().lower()).replace(" ", "")


def _fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        if resp.status_code >= 400:
            return None
        return resp.text
    except requests.RequestException:
        return None


def _extraer_cards(html: str) -> list[dict]:
    """Ancla en la línea de rating (universal en toda la red dir.ar) y toma
    las 2 líneas anteriores como nombre/dirección — no necesita conocer las
    categorías reales de cada rubro, a diferencia del parser original de
    solo-logística."""
    texto = TAG_RE.sub("\n", html)
    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    cards = []
    for i, linea in enumerate(lineas):
        m = RATING_RE.match(linea)
        if not m or i < 2:
            continue
        direccion = lineas[i - 1]
        nombre = lineas[i - 2]
        cards.append({"nombre": nombre, "direccion": direccion,
                       "rating": m.group(1), "resenas": int(m.group(2))})
    return cards


def buscar_por_zona_y_dominio(zona: str, dominio: str) -> dict:
    if dominio not in DOMINIOS:
        return {"zona": zona, "dominio": dominio, "error": f"dominio no reconocido: {dominio}", "nuevas": 0}
    if es_zona_prohibida(zona):
        return {"zona": zona, "dominio": dominio, "error": "zona prohibida (CABA)", "nuevas": 0}

    slug = _slug_de_zona(zona)
    url = f"https://{dominio}/ciudad/{slug}.html"
    html = _fetch(url)
    if html is None:
        _marcar_procesado(zona, dominio, 0)
        return {"zona": zona, "dominio": dominio, "error": "no se pudo descargar la página (slug o dominio a revisar)", "nuevas": 0}

    cards = _extraer_cards(html)
    if not cards:
        _marcar_procesado(zona, dominio, 0)
        return {"zona": zona, "dominio": dominio, "error": "0 cards — revisar con main.py auditar-directorios", "nuevas": 0}

    rubro_pista = DOMINIOS[dominio]
    conn = get_conn()
    nuevas = 0
    descartadas = 0
    for c in cards:
        nombre = c["nombre"]
        if not _parece_empresa(nombre, zona, texto_extra=c["direccion"]):
            descartadas += 1
            continue
        if es_cadena_excluida(nombre):
            descartadas += 1
            continue
        if _ya_existe_en_db(nombre, conn) or _ya_descubierta(nombre, zona, conn):
            continue
        snippet = f"{dominio} ({rubro_pista}) — {c['direccion']} — {c['rating']}★ ({c['resenas']} reseñas)"
        conn.execute(
            "INSERT INTO discovered_companies_raw (nombre_crudo, url, snippet, zona, query_id, estado, creado_en) "
            "VALUES (?, ?, ?, ?, NULL, 'DISCOVERED', ?)",
            (nombre, url, snippet, zona, now()),
        )
        nuevas += 1
    conn.commit()
    conn.close()
    _marcar_procesado(zona, dominio, nuevas)
    return {"zona": zona, "dominio": dominio, "nuevas": nuevas, "descartadas": descartadas, "total_cards": len(cards)}


def _marcar_procesado(zona: str, dominio: str, nuevas: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO directorio_dir_ar_progress (zona, dominio, empresas_nuevas, procesado_en) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(zona, dominio) DO UPDATE SET empresas_nuevas=empresas_nuevas+excluded.empresas_nuevas, procesado_en=excluded.procesado_en",
        (zona, dominio, nuevas, now()),
    )
    conn.commit()
    conn.close()


def combinaciones_pendientes(zonas: list[str]) -> list[tuple[str, str]]:
    """(zona, dominio) todavía no probados — el contenido de un directorio no
    cambia tan rápido como para justificar re-leerlo cada hora para siempre."""
    conn = get_conn()
    ya_hechas = {(r["zona"], r["dominio"]) for r in conn.execute("SELECT zona, dominio FROM directorio_dir_ar_progress")}
    conn.close()
    return [(z, d) for z in zonas for d in DOMINIOS if (z, d) not in ya_hechas]
