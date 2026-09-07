"""Crawler directo de logistica.dir.ar — directorio real de empresas de
logística/transporte/mensajería/mudanzas de Argentina, organizado por ciudad,
con dirección y a veces teléfono publicado y verificado. Encontrado por el
usuario: una sola página de ciudad (ej. /ciudad/hurlingham.html) trae 30-60
empresas reales de una vez, gratis, sin gastar presupuesto de Serper — mismo
espíritu que Overpass, pero con datos de mucha mejor calidad (verificado por
el propio directorio, con rating y cantidad de reseñas).

Estructura de cada card en la página (confirmado por el usuario, pegando el
contenido real renderizado): un bloque repetido de 4 líneas:
    <categoría> (ej. "Logística", "Transporte de carga", "Mudanzas")
    <nombre de la empresa>
    <dirección>
    ★ <rating> (<cantidad de reseñas>)

No se pudo verificar el HTML real desde este entorno (sin acceso a
internet) — el parser está armado a partir del texto tal como se pegó, y
debe confirmarse corriéndolo de verdad en una PC con conexión. Si falla,
devuelve lista vacía en vez de romper (nunca inventa datos).
"""
import re

import requests

from app.db import get_conn, now
from app.discovery import _parece_empresa, _ya_existe_en_db, _ya_descubierta, _quitar_acentos
from app.exclusions import es_cadena_excluida, es_zona_prohibida

BASE_URL = "https://logistica.dir.ar/ciudad/{slug}.html"
USER_AGENT = "MotorDeJackpots/1.0 (uso personal, busqueda de empleo)"
TIMEOUT = 15

TAG_RE = re.compile(r"<[^>]+>")
CATEGORIAS_VALIDAS = {
    "logistica", "transporte de carga", "mensajeria y envios", "mudanzas",
    "correo y servicios postales", "transporte ferroviario",
}
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
    """Convierte el HTML a texto plano y agrupa de a 4 líneas no vacías
    (categoría, nombre, dirección, rating) — resiliente a espacios extra
    generados por el strip de tags, pero asume ese orden fijo."""
    texto = TAG_RE.sub("\n", html)
    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    cards = []
    i = 0
    while i < len(lineas) - 3:
        categoria_norm = _quitar_acentos(lineas[i].lower())
        if categoria_norm in CATEGORIAS_VALIDAS:
            nombre, direccion, posible_rating = lineas[i + 1], lineas[i + 2], lineas[i + 3]
            m = RATING_RE.match(posible_rating)
            if m:
                cards.append({"categoria": lineas[i], "nombre": nombre, "direccion": direccion,
                               "rating": m.group(1), "resenas": int(m.group(2))})
                i += 4
                continue
        i += 1
    return cards


def buscar_por_zona(zona: str) -> dict:
    if es_zona_prohibida(zona):
        return {"zona": zona, "error": "zona prohibida (CABA)", "nuevas": 0}

    slug = _slug_de_zona(zona)
    html = _fetch(BASE_URL.format(slug=slug))
    if html is None:
        return {"zona": zona, "error": "no se pudo descargar la página (revisar el slug de la URL a mano)", "nuevas": 0}

    cards = _extraer_cards(html)
    if not cards:
        return {"zona": zona, "error": "0 cards extraídas — el parser no coincide con el HTML real, revisar a mano", "nuevas": 0}

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
        snippet = f"logistica.dir.ar ({c['categoria']}) — {c['direccion']} — {c['rating']}★ ({c['resenas']} reseñas)"
        conn.execute(
            "INSERT INTO discovered_companies_raw (nombre_crudo, url, snippet, zona, query_id, estado, creado_en) "
            "VALUES (?, ?, ?, ?, NULL, 'DISCOVERED', ?)",
            (nombre, BASE_URL.format(slug=slug), snippet, zona, now()),
        )
        nuevas += 1
    conn.commit()
    conn.close()
    return {"zona": zona, "nuevas": nuevas, "descartadas": descartadas, "total_cards": len(cards)}
