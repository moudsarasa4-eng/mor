"""Geocodificación real vía OpenStreetMap Nominatim — gratis, sin API key
(a diferencia de Google Maps). Respeta la política de uso de Nominatim:
máximo 1 request/segundo, con User-Agent identificable.

Calcula coordenadas (lat/lon) y distancia en línea recta (haversine, metros/km)
entre el domicilio de Marco y cada empresa con dirección conocida. Esto NO
reemplaza el tiempo real de viaje en colectivo/tren (para eso hace falta un
motor de rutas como OSRM, no incluido) — es un dato objetivo adicional para
descartar casos obviamente lejos antes de estimar el viaje real a mano.
"""
import time
from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2

import requests

from app.db import get_conn, now

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "MotorDeJackpots/1.0 (uso personal, busqueda de empleo)"

ORIGEN_DIRECCION = "Rosas Castillo 1698, Hurlingham, Buenos Aires, Argentina"

_ultimo_request = 0.0


def _rate_limit():
    global _ultimo_request
    transcurrido = time.monotonic() - _ultimo_request
    if transcurrido < 1.0:
        time.sleep(1.0 - transcurrido)
    _ultimo_request = time.monotonic()


@dataclass
class Coordenadas:
    lat: float
    lon: float
    direccion_encontrada: str


def geocodificar(direccion: str) -> Coordenadas | None:
    _rate_limit()
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": direccion, "format": "json", "limit": 1, "countrycodes": "ar"},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        resultados = resp.json()
    except requests.RequestException:
        return None

    if not resultados:
        return None
    r = resultados[0]
    return Coordenadas(lat=float(r["lat"]), lon=float(r["lon"]), direccion_encontrada=r.get("display_name", direccion))


def distancia_haversine_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  # radio de la Tierra en metros
    p1, p2 = radians(lat1), radians(lat2)
    dp = radians(lat2 - lat1)
    dl = radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def _origen_cacheado() -> Coordenadas | None:
    conn = get_conn()
    row = conn.execute("SELECT lat, lon FROM origen_cache WHERE id=1").fetchone()
    conn.close()
    if row:
        return Coordenadas(lat=row["lat"], lon=row["lon"], direccion_encontrada=ORIGEN_DIRECCION)
    coords = geocodificar(ORIGEN_DIRECCION)
    if coords:
        conn = get_conn()
        conn.execute("INSERT OR REPLACE INTO origen_cache (id, lat, lon, creado_en) VALUES (1, ?, ?, ?)",
                     (coords.lat, coords.lon, now()))
        conn.commit()
        conn.close()
    return coords


def calcular_distancia_a_empresa(direccion_empresa: str) -> dict | None:
    """Devuelve {lat, lon, distancia_metros, distancia_km} o None si no se pudo
    geocodificar (dirección insuficiente, o Nominatim sin respuesta)."""
    origen = _origen_cacheado()
    if origen is None:
        return None
    destino = geocodificar(direccion_empresa)
    if destino is None:
        return None
    metros = distancia_haversine_metros(origen.lat, origen.lon, destino.lat, destino.lon)
    return {
        "lat": destino.lat, "lon": destino.lon,
        "distancia_metros": round(metros),
        "distancia_km": round(metros / 1000, 2),
        "direccion_resuelta": destino.direccion_encontrada,
    }
