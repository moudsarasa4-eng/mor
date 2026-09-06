"""Fuente de descubrimiento independiente de Serper: OpenStreetMap Overpass
API. Gratis, sin API key, sin límite de presupuesto de por vida (a diferencia
de Serper, que tiene 2500 búsquedas gratis). Busca comercios/oficinas/
industrias reales por categoría y radio geográfico alrededor de una zona,
en vez de por texto — cubre lo que un buscador de texto puede no indexar
(un galpón industrial chico sin sitio web, por ejemplo).

Respeta la política de uso pública de Overpass: sin paralelizar requests,
timeout razonable, un radio acotado por corrida.
"""
import requests

from app.db import get_conn, now
import app.geocoding as geocoding
from app.discovery import _parece_empresa, _ya_existe_en_db, _ya_descubierta
from app.exclusions import es_cadena_excluida, es_zona_prohibida

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "MotorDeJackpots/1.0 (uso personal, busqueda de empleo)"


# tags específicos que de verdad se corresponden con los 4 rubros del CV.
# Bug real encontrado con datos de producción: usar "shop" y "office" SIN
# valor (bare tag) trae CUALQUIER comercio/oficina en el radio — joyería,
# zapatería, peluquería, remisería, panadería, ropa — pura noise sin
# relación con logística/administrativo/atención al cliente/limpieza.
TAGS_RELEVANTES = [
    ('landuse', 'industrial'), ('building', 'industrial'), ('industrial', None),
    ('office', 'logistics'), ('office', 'company'), ('office', 'cleaning'),
    ('shop', 'supermarket'), ('shop', 'wholesale'), ('shop', 'department_store'),
    ('shop', 'laundry'),
]


def _construir_query_overpass(lat: float, lon: float, radio_metros: int) -> str:
    bloques = []
    for clave, valor in TAGS_RELEVANTES:
        filtro = f'["{clave}"="{valor}"]' if valor else f'["{clave}"]'
        bloques.append(f'node{filtro}(around:{radio_metros},{lat},{lon});')
        bloques.append(f'way{filtro}(around:{radio_metros},{lat},{lon});')
    cuerpo = "\n  ".join(bloques)
    return f"[out:json][timeout:25];\n(\n  {cuerpo}\n);\nout center tags;"


def zonas_pendientes(zonas: list[str]) -> list[str]:
    """OSM no cambia rápido (a diferencia de una búsqueda de texto), así que
    no tiene sentido re-consultar la misma zona cada hora en el ciclo
    automático — una vez es suficiente hasta que se pida explícitamente de
    nuevo (main.py overpass corre igual, sin este filtro, si se invoca a mano)."""
    conn = get_conn()
    ya_hechas = {r["zona"] for r in conn.execute("SELECT zona FROM overpass_progress").fetchall()}
    conn.close()
    return [z for z in zonas if z not in ya_hechas]


def buscar_por_zona(zona: str, radio_metros: int = 1500) -> dict:
    """Geocodifica la zona, consulta Overpass, filtra y persiste candidatas
    nuevas en discovered_companies_raw (query_id=NULL: no cuenta contra el
    presupuesto de por vida de Serper, que es un recurso distinto)."""
    if es_zona_prohibida(zona):
        return {"zona": zona, "error": "zona prohibida (CABA)", "nuevas": 0}

    coords = geocoding.geocodificar(f"{zona}, Buenos Aires, Argentina")
    if coords is None:
        # se marca igual como "procesada" (aunque haya fallado): si no, esta
        # zona queda primera en zonas_pendientes() para siempre — el ciclo
        # automático la reintentaría cada hora sin avanzar nunca a las
        # zonas siguientes. El comando manual (main.py overpass --zona X)
        # no pasa por zonas_pendientes(), así que sirve para forzar un
        # reintento puntual sin este bloqueo.
        _marcar_procesada(zona, nuevas=0)
        return {"zona": zona, "error": "no se pudo geocodificar la zona", "nuevas": 0}

    query = _construir_query_overpass(coords.lat, coords.lon, radio_metros)
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query},
                              headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        _marcar_procesada(zona, nuevas=0)
        return {"zona": zona, "error": str(e), "nuevas": 0}

    conn = get_conn()
    nuevas = 0
    descartadas = 0
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        nombre = tags.get("name")
        if not nombre:
            continue
        if not _parece_empresa(nombre, zona):
            descartadas += 1
            continue
        if es_cadena_excluida(nombre):
            descartadas += 1
            continue
        if _ya_existe_en_db(nombre, conn) or _ya_descubierta(nombre, zona, conn):
            continue

        calle = tags.get("addr:street", "")
        numero = tags.get("addr:housenumber", "")
        direccion = f"{calle} {numero}".strip() or None
        categoria = tags.get("office") or tags.get("shop") or tags.get("industrial") or tags.get("landuse") or ""
        snippet = f"OpenStreetMap ({categoria})" + (f" — {direccion}" if direccion else "")

        conn.execute(
            "INSERT INTO discovered_companies_raw (nombre_crudo, url, snippet, zona, query_id, estado, creado_en) "
            "VALUES (?, NULL, ?, ?, NULL, 'DISCOVERED', ?)",
            (nombre, snippet, zona, now()),
        )
        nuevas += 1

    conn.commit()
    conn.close()
    _marcar_procesada(zona, nuevas)
    return {"zona": zona, "nuevas": nuevas, "descartadas": descartadas, "total_osm": len(data.get("elements", []))}


def _marcar_procesada(zona: str, nuevas: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO overpass_progress (zona, empresas_nuevas, procesado_en) VALUES (?, ?, ?) "
        "ON CONFLICT(zona) DO UPDATE SET empresas_nuevas=empresas_nuevas+excluded.empresas_nuevas, procesado_en=excluded.procesado_en",
        (zona, nuevas, now()),
    )
    conn.commit()
    conn.close()
