"""Extrae contacto real DIRECTO del sitio propio de la empresa — más preciso
que un snippet cortado de resultados de búsqueda (lo que hacía contact_finder
hasta ahora, único método disponible). Nunca inventa nada: solo lo que
aparece publicado en el HTML real de la empresa (mailto:, tel:, o datos
estructurados schema.org que la propia empresa publicó).
"""
import json
import re

import requests

TIMEOUT = 6
USER_AGENT = "MotorDeJackpots/1.0 (uso personal, busqueda de empleo)"
RUTAS_CONTACTO = ["", "/contacto", "/contactenos", "/contacto.html", "/nosotros", "/quienes-somos"]

MAILTO_RE = re.compile(r'mailto:([\w.+-]+@[\w-]+\.[\w.-]+)', re.IGNORECASE)
TEL_HREF_RE = re.compile(r'tel:([+\d][\d\s().\-]{6,})', re.IGNORECASE)
LDJSON_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)

EMAILS_RUIDO = ["ejemplo.com", "sentry.io", "wixpress.com", "godaddy.com", "cloudflare.com", "example.com"]


def _limpiar_emails(emails: list[str]) -> list[str]:
    vistos = []
    for e in emails:
        el = e.lower()
        if any(r in el for r in EMAILS_RUIDO):
            continue
        if el not in vistos:
            vistos.append(el)
    return vistos


def _extraer_de_ldjson(html: str) -> dict:
    """Busca bloques schema.org Organization/LocalBusiness con email/telephone
    publicados directamente por la empresa — la fuente más confiable posible
    cuando existe, porque no depende de parsear texto libre."""
    for bloque in LDJSON_RE.findall(html):
        try:
            data = json.loads(bloque)
        except (ValueError, TypeError):
            continue
        candidatos = data if isinstance(data, list) else [data]
        for c in candidatos:
            if not isinstance(c, dict):
                continue
            email = c.get("email")
            tel = c.get("telephone")
            if email or tel:
                return {"email": email, "telefono": tel}
    return {}


def _fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
        if resp.status_code >= 400:
            return None
        return resp.text
    except requests.RequestException:
        return None


def extraer_contacto_de_sitio(dominio: str) -> dict | None:
    """Prueba la home y rutas típicas de contacto, en ese orden. Devuelve
    {email, telefono, fuente_url} con lo primero real que encuentre, o None
    si no hay nada publicado (nunca inventa ni adivina un email por patrón)."""
    if not dominio:
        return None

    if dominio.startswith("http"):
        base = dominio
    else:
        # muchos sitios chicos/viejos no tienen SSL — si https ni siquiera
        # carga la home, se cae a http antes de descartar el sitio entero.
        base = f"https://{dominio}"
        if _fetch(base) is None:
            base = f"http://{dominio}"

    for ruta in RUTAS_CONTACTO:
        url = base.rstrip("/") + ruta
        html = _fetch(url)
        if html is None:
            continue

        ld = _extraer_de_ldjson(html)
        emails_mailto = _limpiar_emails(MAILTO_RE.findall(html))
        telefonos = TEL_HREF_RE.findall(html)

        email = ld.get("email") or (emails_mailto[0] if emails_mailto else None)
        telefono = ld.get("telefono") or (telefonos[0].strip() if telefonos else None)

        if email or telefono:
            return {"email": email, "telefono": telefono, "fuente_url": url}

    return None
