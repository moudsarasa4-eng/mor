"""Verifica que el sitio de una candidata realmente responde (no está caído,
no está parkeado). Antes el motor promovía una candidata solo por aparecer en
un resultado de búsqueda, sin chequear si el link siquiera carga.
"""
import re

import requests

TIMEOUT = 5  # bajo a propósito: se llama por cada candidata nueva dentro de la tanda,
              # un timeout largo puede comerse minutos de la tanda horaria si hay sitios caídos
DOMINIOS_PARKING = ["sedoparking.com", "godaddy.com/park", "domainmarket.com", "afternic.com", "hugedomains.com"]


def sitio_activo(url: str) -> bool | None:
    """True = responde OK, False = caído/error/parkeado, None = no se pudo chequear
    (sin conexión, timeout — no se asume nada en ese caso)."""
    if not url:
        return None
    try:
        resp = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        if resp.status_code >= 400:
            # algunos sitios no soportan HEAD, reintentar con GET liviano
            resp = requests.get(url, timeout=TIMEOUT, allow_redirects=True, stream=True)
            resp.close()
        url_final = resp.url.lower()
        if any(dom in url_final for dom in DOMINIOS_PARKING):
            return False
        return resp.status_code < 400
    except requests.RequestException:
        return None


def extraer_dominio(url: str) -> str:
    m = re.search(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1).lower() if m else ""
