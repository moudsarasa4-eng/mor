"""Ronda de visita presencial: el canal histórico de mayor conversión para
estos rubros (limpieza, logística, administrativo, atención al cliente) en el
conurbano no es un aviso online, es golpear la puerta con el CV impreso. Esto
genera una lista ordenada por distancia real de candidatas sin contacto
todavía, pensada para recorrer a pie/en colectivo en una salida.
"""
from app.db import get_conn


def generar_ronda(limite: int = 8, max_km: float | None = None) -> list[dict]:
    conn = get_conn()
    query = (
        "SELECT c.id, c.nombre, c.zona, c.direccion, c.distancia_km, c.rubro, c.actividad "
        "FROM companies c "
        "WHERE c.estado='candidata' "
        "AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = c.id) "
        "AND NOT EXISTS (SELECT 1 FROM contacts ct WHERE ct.company_id = c.id) "
        "AND c.contacto_intentado_sin_resultado = 1 "  # ya se buscó contacto online y no hay: candidata típica para presencial
        "AND c.direccion IS NOT NULL AND c.distancia_km IS NOT NULL"
    )
    params = []
    if max_km is not None:
        query += " AND c.distancia_km <= ?"
        params.append(max_km)
    query += " ORDER BY c.distancia_km ASC LIMIT ?"
    params.append(limite)

    filas = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(f) for f in filas]


def formatear_ronda_txt(ronda: list[dict]) -> str:
    if not ronda:
        return (
            "No hay candidatas listas para ronda presencial todavía.\n"
            "(Se necesitan candidatas con dirección geocodificada, sin contacto online "
            "encontrado, y sin visita ya registrada.)"
        )
    lineas = [
        "RONDA DE VISITA PRESENCIAL — ordenada por distancia real desde Rosas Castillo 1698, Hurlingham",
        "Llevá: CV impreso (varias copias), DNI. Preguntá por 'encargado de personal' o 'administración'.",
        "=" * 70,
        "",
    ]
    for i, f in enumerate(ronda, 1):
        lineas.append(f"{i}. [{f['id']}] {f['nombre']} — {f['distancia_km']} km")
        lineas.append(f"   Dirección: {f['direccion']}")
        lineas.append(f"   Rubro: {f['rubro']}")
        if f["actividad"]:
            lineas.append(f"   Actividad: {f['actividad']}")
        lineas.append("")
    return "\n".join(lineas)
