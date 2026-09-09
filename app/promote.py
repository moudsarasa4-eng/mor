"""Promueve candidatas de discovered_companies_raw a la tabla companies.

Esto cierra el hueco del pipeline: sin este paso, discovery.py llenaba
discovered_companies_raw pero la tabla companies (y por lo tanto el dashboard,
"empresas verificadas" y "jackpots") quedaba vacía para siempre, sin importar
cuánto buscara el motor.

Importante: esto NO es "verificación" real ni scoring. Crea una empresa con
estado='candidata' (no aparece en el Top de oportunidades, que solo muestra
'jackpot'/'en_revision') a partir de heurísticas simples, para que quede
visible y lista para que un humano o una sesión de Claude Code la revise,
puntúe y audite con criterio real — igual que se hizo con Hurlingham.
"""
import re

from app.db import get_conn, now
from app.keywords import KEYWORDS_SEED
from app.exclusions import es_cadena_excluida, es_zona_prohibida, es_agencia_rrhh
from app.salarios_referencia import estimar_sueldo
import app.site_check as site_check
import app.geocoding as geocoding
from app.discovery import extraer_keywords_de_texto, MAX_KEYWORDS_DESCUBIERTAS, _quitar_acentos, _parece_negocio_unipersonal

# la geocodificación (app/geocoding.py) existía en el código pero nunca se
# llamaba automáticamente — solo por comando manual (main.py geocode). Sin
# eso, ningún homónimo lejano se descartaba nunca por distancia real, sin
# importar cuántos patrones de texto se agregaran. Overpass y la red dir.ar
# sí traen una dirección real en el snippet — se aprovecha acá para
# verificar la ubicación de las candidatas nuevas antes de promoverlas.
_DIRECCION_OVERPASS_RE = re.compile(r"OpenStreetMap \([a-z_]+\) — (.+)$")
_DIRECCION_DIR_AR_RE = re.compile(r"dir\.ar \(\w+\) — (.+?) — [\d,\.]+★")
MAX_DISTANCIA_KM_PLAUSIBLE = 80  # generoso sobre el límite de 50 min en colectivo — margen para no descartar por error


def _extraer_direccion_real(snippet: str) -> str | None:
    snippet = snippet or ""
    for patron in (_DIRECCION_OVERPASS_RE, _DIRECCION_DIR_AR_RE):
        m = patron.search(snippet)
        if m:
            return m.group(1).strip()
    return None


def _ubicacion_implausible(nombre: str, snippet: str, zona: str) -> str | None:
    """None si no se pudo verificar (sin dirección real, o sin red — nunca
    bloquea por falta de datos) o si la distancia es razonable. Si la
    distancia geocodificada es absurda, devuelve el motivo para descartar."""
    direccion = _extraer_direccion_real(snippet)
    if not direccion:
        return None
    resultado = geocoding.calcular_distancia_a_empresa(f"{direccion}, {zona}, Buenos Aires, Argentina")
    if resultado is None:
        return None  # sin red o Nominatim no respondió — no se asume nada
    if resultado["distancia_km"] > MAX_DISTANCIA_KM_PLAUSIBLE:
        return f"ubicación real a {resultado['distancia_km']} km (homónimo probable) — {resultado['direccion_resuelta']}"
    return None

# keyword -> categoria, para inferir el rubro más probable de la candidata
_KEYWORD_A_CATEGORIA = {kw: cat for cat, kws in KEYWORDS_SEED.items() for kw in kws}


def _limpiar_nombre_final(nombre: str) -> str:
    nombre = re.sub(r"\s+", " ", nombre).strip()
    return nombre[:120]


_STOPWORDS_NUCLEO = {"sa", "srl", "sac", "home", "inicio", "buenos", "aires", "argentina",
                     "empresa", "compañía", "compania", "grupo", "quienes", "somos"}


def _nucleo_nombre(nombre: str) -> str:
    """Primeras 2 palabras significativas (sin sufijos societarios ni palabras
    genéricas) — agarra duplicados tipo 'Maquinarias Caseros S.A. Perfil de
    Compañía' vs 'Maquinarias Caseros s.a. | Buenos Aires', que el nombre
    exacto y el dominio solos no siempre pescan."""
    # bug real: "Logística" (con tilde) y "Logistica" (sin tilde) generaban
    # núcleos distintos y el motor promovía la misma empresa dos veces (visto
    # en producción: "Logística Caseros srl" e "Logistica Caseros SRL" como
    # 2 filas separadas) — se saca el acento antes de tokenizar.
    palabras = re.findall(r"[a-z0-9]+", _quitar_acentos(nombre.lower()))
    significativas = [p for p in palabras if p not in _STOPWORDS_NUCLEO and len(p) > 1]
    return " ".join(significativas[:2])


# tag de OSM (ver overpass_discovery.TAGS_RELEVANTES) -> categoría real. Bug
# real encontrado: las candidatas de Overpass no tienen keyword (vienen sin
# query_id, query_id=NULL), así que _inferir_rubro(None) les asignaba
# "logistica" a TODAS por defecto, sin importar que el tag real fuera
# supermarket, laundry, etc.
_TAG_OSM_A_CATEGORIA = {
    "supermarket": "atencion_cliente", "wholesale": "atencion_cliente",
    "department_store": "atencion_cliente", "laundry": "limpieza",
    "cleaning": "limpieza", "logistics": "logistica", "industrial": "logistica",
    "company": "administrativo",
}
_TAG_OSM_RE = re.compile(r"OpenStreetMap \(([a-z_]+)\)")
# app/directorio_dir_ar.py ya guarda el rubro real en el snippet, ej.
# "gimnasios.dir.ar (atencion_cliente) — ..." — no hace falta traducir nada,
# solo extraerlo.
_RUBRO_DIR_AR_RE = re.compile(r"dir\.ar \((\w+)\)|limpiezas\.com\.ar \((\w+)\)")


def _inferir_rubro_por_texto(nombre: str, snippet: str) -> str | None:
    """Fallback cuando no hay keyword de origen (o no calza con ningún
    rubro): busca los términos de KEYWORDS_SEED directo en nombre+snippet.
    Bug real de producción que esto corrige: ejecutar_query() guardaba
    query_id=NULL en TODA candidata durante un tiempo (ver historial de
    discovery.py), así que _inferir_rubro caía SIEMPRE al default
    'logistica' — 1778/1778 candidatas de una corrida real quedaron con ese
    rubro, incluyendo empresas de limpieza, tapizados, atención al cliente,
    etc. Esto da una segunda oportunidad basada en el contenido real, no
    solo en qué búsqueda las encontró."""
    texto = _quitar_acentos(f"{nombre} {snippet}".lower())
    conteos = {}
    for categoria, terminos in KEYWORDS_SEED.items():
        if categoria == "general":
            continue
        n = sum(1 for t in terminos if _quitar_acentos(t.lower()) in texto)
        if n:
            conteos[categoria] = n
    if not conteos:
        return None
    return max(conteos, key=conteos.get)


def _inferir_rubro(keyword: str | None, snippet: str = "", nombre: str = "") -> str:
    if keyword and keyword in _KEYWORD_A_CATEGORIA:
        cat = _KEYWORD_A_CATEGORIA[keyword]
        if cat != "general":
            return cat
    m = _RUBRO_DIR_AR_RE.search(snippet or "")
    if m:
        rubro = m.group(1) or m.group(2)
        if rubro in ("logistica", "limpieza", "administrativo", "atencion_cliente"):
            return rubro
    m = _TAG_OSM_RE.search(snippet or "")
    if m and m.group(1) in _TAG_OSM_A_CATEGORIA:
        return _TAG_OSM_A_CATEGORIA[m.group(1)]
    por_texto = _inferir_rubro_por_texto(nombre, snippet or "")
    if por_texto:
        return por_texto
    return "logistica"  # default conservador; se corrige en la revisión real


def _tipo_fuente(url: str, nombre: str) -> str:
    """Heurística: si el dominio contiene una palabra del nombre, probablemente
    sea el sitio propio de la empresa; si no, es un directorio/agregador."""
    dom = re.sub(r"^https?://(www\.)?", "", url or "").split("/")[0].lower()
    palabras_nombre = [w.lower() for w in re.split(r"\W+", nombre) if len(w) > 3]
    if any(w in dom for w in palabras_nombre):
        return "sitio_propio"
    return "directorio"


def promover_candidatas(zona: str | None = None, limite: int = 100) -> dict:
    conn = get_conn()
    # estado='DISCOVERED' (no solo company_id IS NULL): las excluidas por cadena
    # o zona prohibida quedan con company_id NULL para siempre (nunca se
    # promueven), y sin este filtro se re-evaluaban en cada corrida, cada vez
    # más lento a medida que se acumulan.
    query = "SELECT d.*, q.keyword FROM discovered_companies_raw d " \
            "LEFT JOIN queries_log q ON q.id = d.query_id " \
            "WHERE d.company_id IS NULL AND d.estado = 'DISCOVERED'"
    params = []
    if zona:
        query += " AND d.zona = ?"
        params.append(zona)
    query += " LIMIT ?"
    params.append(limite)

    filas = conn.execute(query, params).fetchall()
    promovidas = 0
    excluidas_cadena = 0
    for f in filas:
        nombre = _limpiar_nombre_final(f["nombre_crudo"])

        cadena = es_cadena_excluida(nombre)
        if cadena:
            conn.execute(
                "UPDATE discovered_companies_raw SET estado=? WHERE id=?",
                (f"EXCLUIDA_CADENA:{cadena}", f["id"]),
            )
            excluidas_cadena += 1
            continue

        zona_prohibida = es_zona_prohibida(f["zona"])
        if zona_prohibida:
            conn.execute(
                "UPDATE discovered_companies_raw SET estado=? WHERE id=?",
                (f"EXCLUIDA_ZONA_PROHIBIDA:{zona_prohibida}", f["id"]),
            )
            excluidas_cadena += 1  # se cuenta junto (mismo motivo: destino inviable)
            continue

        if es_agencia_rrhh(nombre) or es_agencia_rrhh(f["snippet"] or ""):
            conn.execute(
                "UPDATE discovered_companies_raw SET estado='EXCLUIDA_AGENCIA_RRHH' WHERE id=?",
                (f["id"],),
            )
            excluidas_cadena += 1  # mismo motivo: no es el empleador real
            continue

        rubro = _inferir_rubro(f["keyword"], f["snippet"], nombre)
        sueldo_ref = estimar_sueldo(rubro)
        dominio = site_check.extraer_dominio(f["url"]) if f["url"] else ""

        # dedupe: por nombre normalizado O por dominio (agarra casos donde el
        # nombre varía pero es el mismo sitio, ej. "Empresa SA" vs "Empresa S.A. - Inicio")
        existente = conn.execute("SELECT id FROM companies WHERE nombre = ?", (nombre,)).fetchone()
        if not existente and dominio:
            existente = conn.execute("SELECT id FROM companies WHERE dominio = ? AND dominio != ''", (dominio,)).fetchone()
        if not existente:
            nucleo = _nucleo_nombre(nombre)
            if nucleo:  # solo si quedaron al menos 1-2 palabras significativas, para no matchear todo con todo
                candidatas_zona = conn.execute(
                    "SELECT id, nombre FROM companies WHERE zona = ?", (f["zona"],)
                ).fetchall()
                for cand in candidatas_zona:
                    if _nucleo_nombre(cand["nombre"]) == nucleo:
                        existente = cand
                        break

        if existente:
            company_id = existente["id"]
        else:
            motivo_ubicacion = _ubicacion_implausible(nombre, f["snippet"] or "", f["zona"])
            if motivo_ubicacion:
                conn.execute(
                    "UPDATE discovered_companies_raw SET estado=? WHERE id=?",
                    (f"EXCLUIDA_UBICACION:{motivo_ubicacion}"[:120], f["id"]),
                )
                excluidas_cadena += 1  # mismo motivo: destino inviable
                continue

            sitio_ok = site_check.sitio_activo(f["url"]) if f["url"] else None
            tamano = "chica" if _parece_negocio_unipersonal(nombre, f["snippet"]) else "desconocido"
            ts = now()
            cur = conn.execute(
                "INSERT INTO companies (nombre, rubro, zona, localidad, actividad, estado, tamano_estimado, "
                "sueldo_ref_min, sueldo_ref_max, sueldo_ref_fuente, sueldo_ref_confianza, dominio, sitio_activo, "
                "creado_en, actualizado_en) "
                "VALUES (?, ?, ?, ?, ?, 'candidata', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (nombre, rubro, f["zona"], f["zona"], (f["snippet"] or "")[:300], tamano,
                 sueldo_ref["min"] if sueldo_ref else None, sueldo_ref["max"] if sueldo_ref else None,
                 sueldo_ref["fuente"] if sueldo_ref else None, sueldo_ref["confianza"] if sueldo_ref else None,
                 dominio, (1 if sitio_ok else (0 if sitio_ok is False else None)),
                 ts, ts),
            )
            company_id = cur.lastrowid

            # "entramado": la descripción de esta empresa nueva puede mencionar
            # un término que no está en el diccionario semilla (ej. "limpieza
            # de trenes") — se registra para que futuras tandas lo prueben.
            total_descubiertas = conn.execute(
                "SELECT COUNT(*) c FROM keywords WHERE origen='discovered'"
            ).fetchone()["c"]
            if total_descubiertas < MAX_KEYWORDS_DESCUBIERTAS:
                for frase in extraer_keywords_de_texto(f["snippet"] or ""):
                    # inline con la misma conexión: abrir una conexión aparte acá
                    # (como hace registrar_keyword_descubierta) choca con "database
                    # is locked", porque esta transacción todavía no hizo commit.
                    conn.execute(
                        "INSERT OR IGNORE INTO keywords (termino, categoria, origen, creado_en) VALUES (?, ?, 'discovered', ?)",
                        (frase, rubro, now()),
                    )

        if f["url"]:
            ya_tiene_fuente = conn.execute(
                "SELECT id FROM sources WHERE company_id=? AND url=?", (company_id, f["url"])
            ).fetchone()
            if not ya_tiene_fuente:
                conn.execute(
                    "INSERT INTO sources (company_id, url, tipo, descripcion, creado_en) VALUES (?, ?, ?, ?, ?)",
                    (company_id, f["url"], _tipo_fuente(f["url"], nombre), f["snippet"] or "", now()),
                )

        conn.execute(
            "UPDATE discovered_companies_raw SET company_id=?, estado='RELEVANT' WHERE id=?",
            (company_id, f["id"]),
        )
        promovidas += 1

    conn.commit()
    conn.close()
    return {"zona": zona, "candidatas_evaluadas": len(filas), "promovidas": promovidas,
            "excluidas_cadena": excluidas_cadena}
