"""Auditoría de los subdominios de dir.ar sumados a plantillas_query() (varios
con slug adivinado por búsqueda, sin verificar contra el sitio real porque
WebFetch a dir.ar está bloqueado en el sandbox de desarrollo). Junta el
rendimiento real (yield_score de queries_log) por dominio, para que se pueda
detectar un slug equivocado (0 resultados sostenidos = probablemente el
subdominio no existe o el slug está mal) en vez de asumir que anda solo
porque no tira error.
"""
import re

from app.db import get_conn

DOMINIOS_DIR_AR = [
    "logistica.dir.ar", "limpieza.dir.ar", "limpiezas.com.ar",
    "administraciondeconsorcios.dir.ar", "catering.dir.ar", "gimnasios.dir.ar",
    "tiendasderopa.dir.ar", "saludybelleza.dir.ar", "seguridaddelhogar.dir.ar",
    "talleresmecanicos.dir.ar", "graficaseimprentas.dir.ar", "abogados.dir.ar",
    "transporte.dir.ar",
]


def reporte_dominios() -> list[dict]:
    conn = get_conn()
    resultado = []
    for dominio in DOMINIOS_DIR_AR:
        patron = f"%site:{dominio}%"
        row = conn.execute(
            "SELECT COUNT(*) intentos, COALESCE(SUM(resultados), 0) resultados_totales, "
            "COALESCE(SUM(empresas_nuevas), 0) nuevas_totales "
            "FROM queries_log WHERE query LIKE ?",
            (patron,),
        ).fetchone()
        resultado.append({
            "dominio": dominio,
            "intentos": row["intentos"],
            "resultados_totales": row["resultados_totales"],
            "nuevas_totales": row["nuevas_totales"],
            "sospechoso": row["intentos"] >= 5 and row["resultados_totales"] == 0,
        })
    conn.close()
    return resultado


def formatear_reporte(filas: list[dict]) -> str:
    lineas = ["AUDITORÍA DE DOMINIOS dir.ar/red de directorios", "=" * 60, ""]
    for f in filas:
        estado = "⚠ SOSPECHOSO (probablemente el slug está mal)" if f["sospechoso"] else "OK"
        lineas.append(
            f"{f['dominio']:35} intentos={f['intentos']:4} resultados={f['resultados_totales']:4} "
            f"nuevas={f['nuevas_totales']:4}  {estado}"
        )
    lineas.append("")
    lineas.append(
        "'intentos'=0 significa que todavía no se probó esa keyword+zona. "
        "'sospechoso' con 5+ intentos y 0 resultados en total sugiere que el "
        "subdominio no existe o el slug adivinado está mal — conviene "
        "verificarlo con WebSearch (\"site:<dominio>\") antes de seguir "
        "gastando presupuesto ahí."
    )
    return "\n".join(lineas)
