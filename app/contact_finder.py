"""Busca contacto real de una empresa (nunca de una persona) con esta
prioridad, porque toda fábrica necesita vender por algún canal:

    1. email de administración/info/contacto (de la propia empresa)
    2. página de contacto/formulario propia
    3. teléfono de compras/administración

Corre una query extra por empresa ("<nombre> contacto"), extrae emails y
teléfonos de los snippets con regex, y guarda el mejor hallazgo con
verificado=False (viene de un snippet de búsqueda, no de haber entrado al
sitio) — queda marcado como pendiente de confirmación, nunca se asume cierto.
"""
import re

from app.db import get_conn, now
from app.discovery import _es_dominio_excluido
from app.search_client import buscar, SearchClientError
from app.company import add_contact, add_source
from app.run_state import registrar_queries
from app.contact_verify import verificar_email

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
TEL_RE = re.compile(r"(?:\+?54\s?)?(?:0?11|0?[2-9]\d{1,3})[\s.\-]?\d{3,4}[\s.\-]?\d{4}")

# emails que casi seguro son genéricos de una plataforma, no de la empresa buscada
EMAILS_RUIDO = ["ejemplo.com", "sentry.io", "wixpress.com", "godaddy.com", "cloudflare.com"]

PALABRAS_PRIORIDAD_ALTA = ["administracion", "administración", "info@", "contacto@"]
PALABRAS_COMPRAS = ["compras", "ventas", "comercial"]


def _limpiar_emails(emails: list[str]) -> list[str]:
    return [e for e in emails if not any(ruido in e.lower() for ruido in EMAILS_RUIDO)]


def _priorizar_email(emails: list[str]) -> str | None:
    if not emails:
        return None
    for patron in PALABRAS_PRIORIDAD_ALTA:
        for e in emails:
            if patron in e.lower():
                return e
    return emails[0]


def buscar_contacto(company_id: int, nombre_empresa: str, zona: str) -> dict | None:
    query = f'"{nombre_empresa}" contacto OR administración OR compras'
    try:
        crudo = buscar(query)
    except SearchClientError:
        return None

    conn = get_conn()
    conn.execute(
        "INSERT INTO queries_log (query, zona, keyword, tipo, resultados, empresas_nuevas, duplicados, yield, creado_en) "
        "VALUES (?, ?, '', 'TYPE_CONTACT', ?, 0, 0, 0, ?)",
        (query, zona, len(crudo.get("organic", [])), now()),
    )
    conn.commit()
    conn.close()
    registrar_queries(1)

    emails_encontrados = []
    mejor_url = None
    mejor_tipo_texto = None
    for item in crudo.get("organic", []):
        url = item.get("link", "")
        if _es_dominio_excluido(url):
            continue
        texto = f"{item.get('title', '')} {item.get('snippet', '')}"
        emails = _limpiar_emails(EMAIL_RE.findall(texto))
        if emails:
            emails_encontrados.extend(emails)
            if mejor_url is None:
                mejor_url = url
                mejor_tipo_texto = texto.lower()

    email = _priorizar_email(emails_encontrados)
    if email:
        fuente_id = add_source(company_id, mejor_url or "", tipo="directorio", descripcion="Contacto encontrado por búsqueda")
        mx_ok = verificar_email(email)  # None si no se pudo chequear (sin red) — nunca se asume
        try:
            add_contact(company_id, "email", email, verificado=False, fuente_id=fuente_id, mx_verificado=mx_ok)
        except ValueError:
            return None  # add_contact rechazó (parece nombre de persona)
        prioridad = "administración/info" if any(p in email.lower() for p in PALABRAS_PRIORIDAD_ALTA) else "general"
        return {"tipo": "email", "valor": email, "prioridad": prioridad, "fuente": mejor_url, "mx_verificado": mx_ok}

    # sin email: buscar teléfono como último recurso
    for item in crudo.get("organic", []):
        texto = f"{item.get('title', '')} {item.get('snippet', '')}"
        tel_match = TEL_RE.search(texto)
        if tel_match:
            fuente_id = add_source(company_id, item.get("link", ""), tipo="directorio", descripcion="Teléfono encontrado por búsqueda")
            add_contact(company_id, "telefono", tel_match.group(0), verificado=False, fuente_id=fuente_id)
            return {"tipo": "telefono", "valor": tel_match.group(0), "prioridad": "general", "fuente": item.get("link", "")}

    return None


def correr_lote(zona: str | None = None, limite: int = 20) -> dict:
    """Busca contacto para candidatas que todavía no tienen ninguno."""
    conn = get_conn()
    query = (
        "SELECT c.id, c.nombre, c.zona FROM companies c "
        "WHERE c.estado='candidata' AND NOT EXISTS (SELECT 1 FROM contacts ct WHERE ct.company_id = c.id)"
    )
    params = []
    if zona:
        query += " AND c.zona = ?"
        params.append(zona)
    query += " LIMIT ?"
    params.append(limite)
    filas = conn.execute(query, params).fetchall()
    conn.close()

    encontrados = 0
    detalle = []
    for f in filas:
        r = buscar_contacto(f["id"], f["nombre"], f["zona"])
        if r:
            encontrados += 1
            detalle.append({"empresa": f["nombre"], **r})

    return {"procesadas": len(filas), "contactos_encontrados": encontrados, "detalle": detalle}
