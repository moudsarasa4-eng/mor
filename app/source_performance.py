"""Mide qué tipos de fuente (sitio_propio, directorio, noticia, otro) producen
empresas verificadas y jackpots reales, a partir de los datos ya cargados en la DB.
No inventa pesos iniciales: todo se calcula de datos observados.
"""
from app.db import get_conn


def source_quality_report() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.tipo,
               COUNT(DISTINCT s.company_id) as empresas_con_esta_fuente,
               SUM(CASE WHEN c.estado = 'jackpot' THEN 1 ELSE 0 END) as jackpots,
               SUM(CASE WHEN c.estado = 'descartada' THEN 1 ELSE 0 END) as descartadas
        FROM sources s
        JOIN companies c ON c.id = s.company_id
        GROUP BY s.tipo
        ORDER BY jackpots DESC
    """).fetchall()
    conn.close()

    resultado = []
    for r in rows:
        total = r["empresas_con_esta_fuente"]
        jackpot_rate = round(r["jackpots"] / total * 100, 1) if total else 0.0
        resultado.append({
            "tipo_fuente": r["tipo"],
            "empresas": total,
            "jackpots": r["jackpots"],
            "descartadas": r["descartadas"],
            "jackpot_rate_pct": jackpot_rate,
            "muestra_suficiente": total >= 10,  # umbral mínimo antes de sacar conclusiones
        })
    return resultado


if __name__ == "__main__":
    import json
    print(json.dumps(source_quality_report(), ensure_ascii=False, indent=2))
