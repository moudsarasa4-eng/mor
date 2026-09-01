"""Sistema de aprendizaje — analiza resultados reales de outreach para sugerir
ajustes de pesos. No los aplica solo: imprime una recomendación para revisión humana.
"""
from app.db import get_conn

RESPUESTA_POSITIVA = {"respondio", "entrevista", "contratacion"}


def analizar_resultados(minimo_casos: int = 20) -> dict:
    conn = get_conn()
    rows = conn.execute("""
        SELECT o.estado as outreach_estado, s.employer_score, s.hiring_signal_score,
               s.opportunity_score, s.accessibility_score, s.contactability_score, s.jackpot_score
        FROM outreach o
        JOIN companies c ON c.id = o.company_id
        JOIN scores s ON s.company_id = c.id
        WHERE o.estado != 'generado'
    """).fetchall()
    conn.close()

    total = len(rows)
    if total < minimo_casos:
        return {"suficientes_datos": False, "casos": total, "minimo_requerido": minimo_casos}

    positivos = [r for r in rows if r["outreach_estado"] in RESPUESTA_POSITIVA]
    negativos = [r for r in rows if r["outreach_estado"] not in RESPUESTA_POSITIVA]

    def promedio(rows_subset, campo):
        if not rows_subset:
            return 0
        return sum(r[campo] for r in rows_subset) / len(rows_subset)

    campos = ["employer_score", "hiring_signal_score", "opportunity_score", "accessibility_score", "contactability_score"]
    comparacion = {
        campo: {
            "promedio_en_positivos": round(promedio(positivos, campo), 1),
            "promedio_en_negativos": round(promedio(negativos, campo), 1),
        }
        for campo in campos
    }

    sugerencias = []
    for campo, valores in comparacion.items():
        diff = valores["promedio_en_positivos"] - valores["promedio_en_negativos"]
        if diff > 10:
            sugerencias.append(f"Aumentar peso de {campo}: correlaciona con respuestas positivas (+{diff:.1f}).")
        elif diff < -10:
            sugerencias.append(f"Revisar peso de {campo}: los casos con score alto en este campo NO están respondiendo mejor ({diff:.1f}).")

    return {
        "suficientes_datos": True,
        "casos": total,
        "positivos": len(positivos),
        "negativos": len(negativos),
        "tasa_respuesta_positiva": round(len(positivos) / total * 100, 1),
        "comparacion": comparacion,
        "sugerencias": sugerencias,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analizar_resultados(), ensure_ascii=False, indent=2))
