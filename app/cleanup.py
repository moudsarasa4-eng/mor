"""Limpieza retroactiva: aplica los filtros de calidad actuales (app.discovery
._parece_empresa, exclusiones de cadena/zona) sobre lo que YA está cargado en
companies. Necesario porque un fix a los filtros de descubrimiento no limpia
solo lo que se cargó antes del fix — esto lo hace explícitamente.

Solo toca candidatas sin puntuar todavía (estado='candidata') y sin outreach
generado — nunca borra ni reclasifica algo que ya se auditó o contactó.
"""
from app.db import get_conn, now
from app.discovery import _parece_empresa
from app.exclusions import es_cadena_excluida, es_zona_prohibida, es_agencia_rrhh


def limpiar_candidatas_basura(zona: str | None = None) -> dict:
    conn = get_conn()
    query = (
        "SELECT id, nombre, zona, actividad FROM companies "
        "WHERE estado='candidata' AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = companies.id)"
    )
    params = []
    if zona:
        query += " AND zona = ?"
        params.append(zona)
    filas = conn.execute(query, params).fetchall()

    limpiadas = []
    for f in filas:
        motivo = None
        cadena = es_cadena_excluida(f["nombre"])
        if cadena:
            motivo = f"Limpieza retroactiva: cadena excluida ({cadena})"
        elif es_zona_prohibida(f["zona"]):
            motivo = f"Limpieza retroactiva: zona prohibida ({f['zona']})"
        elif es_agencia_rrhh(f["nombre"]) or es_agencia_rrhh(f["actividad"] or ""):
            motivo = "Limpieza retroactiva: agencia de RRHH/staffing, no es el empleador real"
        elif not _parece_empresa(f["nombre"], f["zona"]):
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
