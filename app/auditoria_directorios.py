"""Auditoría de los subdominios de la red dir.ar que lee app/directorio_dir_ar.py
(varios con slug adivinado por búsqueda, sin verificar contra el sitio real
porque WebFetch a dir.ar está bloqueado en el sandbox de desarrollo). Junta el
rendimiento real (directorio_dir_ar_progress) por dominio, para poder
detectar un slug equivocado (0 resultados sostenidos en varias zonas =
probablemente el subdominio no existe o el slug está mal) en vez de asumir
que anda solo porque no tira error.

Nota: antes esto leía queries_log buscando "site:<dominio>" — quedó
desactualizado cuando esas búsquedas por Serper se sacaron de keywords.py
(app/directorio_dir_ar.py lee el sitio directo y gratis, sin pasar por
Serper). Ahora lee directorio_dir_ar_progress, que es la tabla real que
usa ese módulo.
"""
from app.db import get_conn
from app.directorio_dir_ar import DOMINIOS as DOMINIOS_DIR_AR


def reporte_dominios() -> list[dict]:
    conn = get_conn()
    resultado = []
    for dominio in DOMINIOS_DIR_AR:
        row = conn.execute(
            "SELECT COUNT(*) intentos, COALESCE(SUM(empresas_nuevas), 0) nuevas_totales "
            "FROM directorio_dir_ar_progress WHERE dominio = ?",
            (dominio,),
        ).fetchone()
        resultado.append({
            "dominio": dominio,
            "intentos": row["intentos"],
            "nuevas_totales": row["nuevas_totales"],
            "sospechoso": row["intentos"] >= 5 and row["nuevas_totales"] == 0,
        })
    conn.close()
    return resultado


def formatear_reporte(filas: list[dict]) -> str:
    lineas = ["AUDITORÍA DE DOMINIOS dir.ar/red de directorios", "=" * 60, ""]
    for f in filas:
        estado = "⚠ SOSPECHOSO (probablemente el slug o el dominio está mal)" if f["sospechoso"] else "OK"
        lineas.append(
            f"{f['dominio']:25} zonas_probadas={f['intentos']:4} nuevas={f['nuevas_totales']:4}  {estado}"
        )
    lineas.append("")
    lineas.append(
        "'zonas_probadas'=0 significa que todavía no le tocó el turno en el "
        "loop automático. 'sospechoso' con 5+ zonas probadas y 0 empresas "
        "nuevas en total sugiere que el subdominio no existe o el slug está "
        "mal — conviene verificarlo con WebSearch (\"site:<dominio>\") antes "
        "de seguir gastando ciclos ahí."
    )
    return "\n".join(lineas)
