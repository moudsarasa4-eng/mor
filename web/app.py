"""App web local del Motor de Jackpots. Correr con: python3 main.py (o python3 web/app.py)
Abre http://localhost:5000
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template, request

from app.db import get_conn, init_db
from app.run_state import get_state
from app import runner
from app.dashboard import top_oportunidades

app = Flask(__name__)


def _stats():
    conn = get_conn()
    total_discovered = conn.execute("SELECT COUNT(*) c FROM discovered_companies_raw").fetchone()["c"]
    total_companies = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    jackpots = conn.execute("SELECT COUNT(*) c FROM companies WHERE estado='jackpot'").fetchone()["c"]
    verificadas = conn.execute("SELECT COUNT(*) c FROM sources").fetchone()["c"]
    queries_totales = conn.execute("SELECT COUNT(*) c FROM queries_log").fetchone()["c"]
    conn.close()
    return {
        "empresas_descubiertas": total_discovered,
        "empresas_verificadas": total_companies,
        "jackpots": jackpots,
        "queries_totales": queries_totales,
    }


def _top_table_data(limit=10):
    conn = get_conn()
    rows = conn.execute("""
        SELECT c.id, c.nombre, c.zona, c.rubro, c.estado,
               s.jackpot_score, s.chances_estimadas, s.chances_baja_confianza,
               s.sueldo_min, s.sueldo_max, s.puesto_objetivo
        FROM companies c
        JOIN scores s ON s.id = (SELECT id FROM scores WHERE company_id = c.id ORDER BY creado_en DESC LIMIT 1)
        WHERE c.estado IN ('jackpot', 'en_revision')
        ORDER BY s.chances_estimadas DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        sueldo = "No estimable" if r["sueldo_min"] is None else f"${r['sueldo_min']:,}-${r['sueldo_max']:,}"
        chances = f"{r['chances_estimadas']}%" + ("*" if r["chances_baja_confianza"] else "")
        out.append({
            "id": r["id"], "nombre": r["nombre"], "zona": r["zona"], "rubro": r["rubro"],
            "puesto": r["puesto_objetivo"] or "-", "chances": chances, "sueldo": sueldo,
            "estado": r["estado"],
        })
    return out


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    st = get_state()
    return jsonify({"state": dict(st), "stats": _stats(), "top": _top_table_data()})


@app.route("/api/start", methods=["POST"])
def api_start():
    started = runner.iniciar_en_background()
    return jsonify({"started": started})


@app.route("/api/pause", methods=["POST"])
def api_pause():
    runner.pausar()
    return jsonify({"ok": True})


@app.route("/api/continue", methods=["POST"])
def api_continue():
    runner.continuar()
    return jsonify({"ok": True})


@app.route("/api/company/<int:company_id>")
def api_company(company_id):
    from app.company import get_company
    return jsonify(get_company(company_id))


def run():
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()
