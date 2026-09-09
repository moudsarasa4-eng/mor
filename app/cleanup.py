"""Limpieza retroactiva: aplica los filtros de calidad actuales (app.discovery
._parece_empresa, exclusiones de cadena/zona) sobre lo que YA está cargado en
companies. Necesario porque un fix a los filtros de descubrimiento no limpia
solo lo que se cargó antes del fix — esto lo hace explícitamente.

Solo toca candidatas sin puntuar todavía (estado='candidata') y sin outreach
generado — nunca borra ni reclasifica algo que ya se auditó o contactó.
"""
from app.db import get_conn, now
from app.discovery import _parece_empresa, _es_dominio_excluido
from app.exclusions import es_cadena_excluida, es_zona_prohibida, es_agencia_rrhh


def limpiar_candidatas_basura(zona: str | None = None) -> dict:
    conn = get_conn()
    # trae también la URL de sources: sin esto, _parece_empresa() solo veía
    # nombre+zona y _es_dominio_excluido() nunca se llamaba acá — bug real
    # encontrado con datos de producción: quedaban colgadas candidatas de
    # homónimos extranjeros (Bella Vista en Chile/México/Arkansas/Perú) cuyo
    # nombre por sí solo no delata el país, pero la URL sí (.cl, .mx,
    # "arkansas" en la ruta) — la limpieza retroactiva nunca las agarraba
    # porque nunca miraba la fuente.
    query = (
        "SELECT c.id, c.nombre, c.zona, c.actividad, "
        "(SELECT url FROM sources WHERE company_id=c.id ORDER BY id LIMIT 1) as fuente_url "
        "FROM companies c "
        "WHERE c.estado='candidata' AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = c.id)"
    )
    params = []
    if zona:
        query += " AND c.zona = ?"
        params.append(zona)
    filas = conn.execute(query, params).fetchall()

    limpiadas = []
    for f in filas:
        motivo = None
        url = f["fuente_url"] or ""
        texto_extra = f"{f['actividad'] or ''} {url}"
        cadena = es_cadena_excluida(f["nombre"])
        if cadena:
            motivo = f"Limpieza retroactiva: cadena excluida ({cadena})"
        elif es_zona_prohibida(f["zona"]):
            motivo = f"Limpieza retroactiva: zona prohibida ({f['zona']})"
        elif es_agencia_rrhh(f["nombre"]) or es_agencia_rrhh(f["actividad"] or ""):
            motivo = "Limpieza retroactiva: agencia de RRHH/staffing, no es el empleador real"
        elif url and _es_dominio_excluido(url):
            motivo = f"Limpieza retroactiva: dominio excluido/extranjero ({url})"
        elif not _parece_empresa(f["nombre"], f["zona"], texto_extra=texto_extra):
            motivo = "Limpieza retroactiva: no parece una empresa real (filtro de calidad actualizado)"

        if motivo:
            conn.execute(
                "UPDATE companies SET estado='descartada', motivo_descarte=?, actualizado_en=? WHERE id=?",
                (motivo, now(), f["id"]),
            )
            limpiadas.append({"id": f["id"], "nombre": f["nombre"], "motivo": motivo})

    conn.commit()
    conn.close()
    return {"evaluadas": len(filas), "limpiadas": len(limpiadas), "detalle": limpiadas}


def recalcular_rubros_basura(zona: str | None = None) -> dict:
    """Recalcula el rubro de candidatas ya promovidas usando la versión
    actual de _inferir_rubro (que ahora también cruza nombre+snippet contra
    KEYWORDS_SEED, no solo el keyword de la búsqueda que la encontró).

    Existe porque un bug real (ejecutar_query() en discovery.py guardaba
    query_id=NULL en discovered_companies_raw, ya corregido) dejó candidatas
    YA promovidas con rubro='logistica' aunque el keyword real que las
    originó nunca se haya podido usar — en una corrida real, 1778 de 1778
    candidatas pendientes quedaron así. El fix a discovery.py solo afecta
    candidatas nuevas; esto corrige retroactivamente las que ya están en
    companies con estado='candidata' (nunca toca outreach ya generado, ni
    reclasifica algo ya puntuado/auditado)."""
    from app.promote import _inferir_rubro

    conn = get_conn()
    query = (
        "SELECT c.id, c.nombre, c.zona, c.rubro, c.actividad, "
        "(SELECT url FROM sources WHERE company_id=c.id ORDER BY id LIMIT 1) as fuente_url "
        "FROM companies c "
        "WHERE c.estado='candidata' AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = c.id)"
    )
    params = []
    if zona:
        query += " AND c.zona = ?"
        params.append(zona)
    filas = conn.execute(query, params).fetchall()

    corregidas = []
    for f in filas:
        snippet = f"{f['actividad'] or ''} {f['fuente_url'] or ''}"
        nuevo_rubro = _inferir_rubro(None, snippet, f["nombre"])
        if nuevo_rubro != f["rubro"]:
            conn.execute(
                "UPDATE companies SET rubro=?, actualizado_en=? WHERE id=?",
                (nuevo_rubro, now(), f["id"]),
            )
            corregidas.append({"id": f["id"], "nombre": f["nombre"], "de": f["rubro"], "a": nuevo_rubro})

    conn.commit()
    conn.close()
    return {"evaluadas": len(filas), "corregidas": len(corregidas), "detalle": corregidas}
