"""Enriquecimiento de contacto SIN gastar Serper.

El contacto es el entregable real: una candidata sin forma de contactarla no
le sirve a Marco. Buscar contacto con Serper (app.contact_finder) gasta
presupuesto de por vida. Pero el sitio propio de la empresa se puede crawlear
gratis (app.site_crawler), y muchas fábricas/pymes publican su email de
administración/ventas ahí mismo.

Este módulo hace la pasada GRATIS: para toda candidata con dominio y sin
contacto, entra al sitio (una request, sin costo) y guarda lo que encuentre
publicado. Nunca inventa un email por patrón — solo lo que está escrito en el
sitio. Recién si esto no encuentra nada se justifica escalar al find-contacts
pago (decisión aparte, deliberada).

Respeta contacto_intentado_sin_resultado: si el crawl gratis no encontró
nada, marca la candidata para no re-crawlear el mismo sitio muerto cada
corrida (el find-contacts pago también respeta ese flag).
"""
from app.db import get_conn, now
from app.site_crawler import extraer_contacto_de_sitio
from app.contact_verify import verificar_email


def enriquecer_contacto_gratis(zona: str | None = None, limite: int = 25) -> dict:
    """Crawlea el sitio propio (gratis) de candidatas con dominio y sin
    contacto. Devuelve cuántas consiguieron contacto nuevo."""
    conn = get_conn()
    query = (
        "SELECT id, nombre, dominio FROM companies "
        "WHERE estado='candidata' AND dominio IS NOT NULL AND dominio != '' "
        "AND contacto_intentado_sin_resultado = 0 "
        "AND NOT EXISTS (SELECT 1 FROM contacts c WHERE c.company_id = companies.id) "
        "AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = companies.id)"
    )
    params = []
    if zona:
        query += " AND zona = ?"
        params.append(zona)
    query += " ORDER BY triage_score DESC NULLS LAST, id DESC LIMIT ?"
    params.append(limite)
    filas = conn.execute(query, params).fetchall()
    conn.close()

    con_contacto = 0
    sin_nada = 0
    for f in filas:
        directo = extraer_contacto_de_sitio(f["dominio"])
        conn = get_conn()
        if directo and (directo.get("email") or directo.get("telefono")):
            cur = conn.execute(
                "INSERT INTO sources (company_id, url, tipo, descripcion, creado_en) VALUES (?, ?, 'sitio_propio', ?, ?)",
                (f["id"], directo["fuente_url"], "contacto extraído del sitio propio (gratis, sin Serper)", now()),
            )
            fuente_id = cur.lastrowid
            if directo.get("email"):
                mx = verificar_email(directo["email"])
                conn.execute(
                    "INSERT INTO contacts (company_id, tipo, valor, verificado, fuente_id, es_persona, mx_verificado, creado_en) "
                    "VALUES (?, 'email', ?, ?, ?, 0, ?, ?)",
                    (f["id"], directo["email"], 1 if mx else 0, fuente_id, 1 if mx else 0, now()),
                )
            if directo.get("telefono"):
                conn.execute(
                    "INSERT INTO contacts (company_id, tipo, valor, verificado, fuente_id, es_persona, creado_en) "
                    "VALUES (?, 'telefono', ?, 1, ?, 0, ?)",
                    (f["id"], directo["telefono"], fuente_id, now()),
                )
            con_contacto += 1
        else:
            conn.execute(
                "UPDATE companies SET contacto_intentado_sin_resultado=1, actualizado_en=? WHERE id=?",
                (now(), f["id"]),
            )
            sin_nada += 1
        conn.commit()
        conn.close()

    return {"evaluadas": len(filas), "con_contacto_nuevo": con_contacto, "sin_resultado": sin_nada}
