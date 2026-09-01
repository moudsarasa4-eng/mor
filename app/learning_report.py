"""Genera reports/learning_report.md — memoria estratégica legible del motor.

Fase 1 (actual): estadísticas descriptivas reales sobre lo cargado en la DB
(fuentes, señales, rubros, descartes). No ajusta pesos automáticamente todavía
(eso requiere volumen de datos — ver app/learning.py, que ya compara resultados
de outreach cuando hay >=20 casos). Este reporte es la base para decidir, con
criterio humano, qué priorizar en la próxima zona.
"""
from datetime import date
from pathlib import Path

from app.db import get_conn
from app.source_performance import source_quality_report

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"


def _mejores_señales(conn, min_muestra=1) -> list[dict]:
    rows = conn.execute("""
        SELECT sig.tipo,
               COUNT(DISTINCT sig.company_id) as casos,
               SUM(CASE WHEN c.estado='jackpot' THEN 1 ELSE 0 END) as jackpots
        FROM signals sig JOIN companies c ON c.id = sig.company_id
        GROUP BY sig.tipo
        HAVING casos >= ?
        ORDER BY jackpots DESC, casos DESC
    """, (min_muestra,)).fetchall()
    out = []
    for r in rows:
        rate = round(r["jackpots"] / r["casos"] * 100, 1) if r["casos"] else 0.0
        out.append({"señal": r["tipo"], "casos": r["casos"], "jackpots": r["jackpots"], "jackpot_rate_pct": rate})
    return out


def _mejores_rubros(conn) -> list[dict]:
    rows = conn.execute("""
        SELECT rubro, COUNT(*) as total, SUM(CASE WHEN estado='jackpot' THEN 1 ELSE 0 END) as jackpots
        FROM companies GROUP BY rubro ORDER BY jackpots DESC
    """).fetchall()
    out = []
    for r in rows:
        rate = round(r["jackpots"] / r["total"] * 100, 1) if r["total"] else 0.0
        out.append({"rubro": r["rubro"], "total": r["total"], "jackpots": r["jackpots"], "jackpot_rate_pct": rate})
    return out


def _mejores_zonas(conn) -> list[dict]:
    rows = conn.execute("""
        SELECT zona, COUNT(*) as total, SUM(CASE WHEN estado='jackpot' THEN 1 ELSE 0 END) as jackpots
        FROM companies GROUP BY zona ORDER BY jackpots DESC
    """).fetchall()
    out = []
    for r in rows:
        rate = round(r["jackpots"] / r["total"] * 100, 1) if r["total"] else 0.0
        out.append({"zona": r["zona"], "total": r["total"], "jackpots": r["jackpots"], "jackpot_rate_pct": rate})
    return out


def _motivos_descarte(conn) -> list[dict]:
    rows = conn.execute("""
        SELECT codigo, COUNT(*) as veces FROM discard_reasons GROUP BY codigo ORDER BY veces DESC
    """).fetchall()
    return [{"motivo": r["codigo"], "veces": r["veces"]} for r in rows]


def generar_reporte() -> str:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    jackpots = conn.execute("SELECT COUNT(*) c FROM companies WHERE estado='jackpot'").fetchone()["c"]
    jackpot_rate = round(jackpots / total * 100, 1) if total else 0.0

    fuentes = source_quality_report()
    señales = _mejores_señales(conn)
    rubros = _mejores_rubros(conn)
    zonas = _mejores_zonas(conn)
    motivos = _motivos_descarte(conn)
    conn.close()

    def tabla(filas, cols, keys):
        if not filas:
            return "_(sin datos todavía)_\n"
        header = "| " + " | ".join(cols) + " |\n"
        header += "| " + " | ".join(["---"] * len(cols)) + " |\n"
        body = "\n".join("| " + " | ".join(str(f[k]) for k in keys) + " |" for f in filas)
        return header + body + "\n"

    md = f"""# MOTOR DE JACKPOTS — LEARNING REPORT
Generado: {date.today().isoformat()}

Empresas analizadas: {total}
Jackpots: {jackpots}
Jackpot rate: {jackpot_rate}%

## Rendimiento por tipo de fuente
{tabla(fuentes, ["Tipo de fuente", "Empresas", "Jackpots", "Jackpot rate"], ["tipo_fuente", "empresas", "jackpots", "jackpot_rate_pct"])}
_Muestra mínima para conclusiones: 10 empresas. Fuentes por debajo de eso son orientativas, no concluyentes._

## Rendimiento por señal de contratación
{tabla(señales, ["Señal", "Casos", "Jackpots", "Jackpot rate"], ["señal", "casos", "jackpots", "jackpot_rate_pct"])}

## Rendimiento por rubro
{tabla(rubros, ["Rubro", "Total", "Jackpots", "Jackpot rate"], ["rubro", "total", "jackpots", "jackpot_rate_pct"])}

## Rendimiento por zona
{tabla(zonas, ["Zona", "Total", "Jackpots", "Jackpot rate"], ["zona", "total", "jackpots", "jackpot_rate_pct"])}

## Motivos de descarte más frecuentes
{tabla(motivos, ["Motivo", "Veces"], ["motivo", "veces"])}

---
_Fase 1: estadísticas descriptivas sobre datos reales cargados. El ajuste automático
de pesos de scoring (app/learning.py) requiere al menos 20 resultados de outreach
reales (respondió/entrevista/contratación vs. no) antes de sugerir cambios — ver
`python3 main.py learning`._
"""

    REPORTS_DIR.mkdir(exist_ok=True)
    out_path = REPORTS_DIR / "learning_report.md"
    out_path.write_text(md, encoding="utf-8")
    return str(out_path)


if __name__ == "__main__":
    print(f"Generado: {generar_reporte()}")
