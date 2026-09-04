"""App web local del Motor de Jackpots. Correr con: python3 main.py (o python3 web/app.py)
Abre http://localhost:5000
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template, request

from app.db import get_conn, init_db
from app.run_state import get_state
from app import runner, scheduler
from app.dashboard import top_oportunidades

app = Flask(__name__)


def _stats():
    conn = get_conn()
    total_discovered = conn.execute("SELECT COUNT(*) c FROM discovered_companies_raw").fetchone()["c"]
    total_companies = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    pendientes = conn.execute("SELECT COUNT(*) c FROM companies WHERE estado='candidata'").fetchone()["c"]
    jackpots = conn.execute("SELECT COUNT(*) c FROM companies WHERE estado='jackpot'").fetchone()["c"]
    queries_totales = conn.execute("SELECT COUNT(*) c FROM queries_log").fetchone()["c"]
    conn.close()
    return {
        "empresas_descubiertas": total_discovered,
        "empresas_verificadas": total_companies,
        "candidatas_pendientes_revision": pendientes,
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
    lifetime = runner.queries_lifetime_usadas()
    presupuesto = runner.CONFIG["discovery"]["lifetime_query_budget"]
    sch_cfg = runner.CONFIG["discovery"]["scheduler"]
    restante = max(0, presupuesto - lifetime)
    corridas_restantes = restante // sch_cfg["queries_per_run"] if sch_cfg["queries_per_run"] else 0
    dias_si_8h = round(corridas_restantes / 8, 1) if corridas_restantes else 0
    dias_si_24h = round(corridas_restantes / 24, 1) if corridas_restantes else 0
    return jsonify({
        "state": dict(st),
        "stats": _stats(),
        "top": _top_table_data(),
        "auto": {
            "activo": scheduler.esta_activo(),
            "proxima_tanda": scheduler.proxima_tanda_en(),
            "intervalo_minutos": sch_cfg["interval_minutes"],
        },
        "presupuesto": {
            "usado": lifetime, "total": presupuesto, "pct": round(lifetime / presupuesto * 100, 1),
            "corridas_restantes": corridas_restantes,
            "dias_estimados_pc_8h": dias_si_8h,
            "dias_estimados_pc_24h": dias_si_24h,
        },
    })


@app.route("/api/auto/start", methods=["POST"])
def api_auto_start():
    started = scheduler.iniciar()
    return jsonify({"started": started})


@app.route("/api/auto/stop", methods=["POST"])
def api_auto_stop():
    scheduler.detener()
    return jsonify({"ok": True})


@app.route("/api/start", methods=["POST"])
def api_start():
    tanda_minutos = runner.CONFIG["discovery"]["tanda_max_minutes"]
    started = runner.iniciar_en_background(max_minutos=tanda_minutos)
    return jsonify({"started": started, "duracion_minutos": tanda_minutos})


@app.route("/api/pause", methods=["POST"])
def api_pause():
    runner.pausar()
    return jsonify({"ok": True})


@app.route("/api/continue", methods=["POST"])
def api_continue():
    runner.continuar()
    return jsonify({"ok": True})


@app.route("/api/export", methods=["POST"])
def api_export():
    from app.export_txt import exportar_candidatas_txt
    archivo = exportar_candidatas_txt()
    return jsonify({"archivo": archivo})


@app.route("/api/candidatas")
def api_candidatas():
    conn = get_conn()
    filtro = "c.estado='candidata' AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = c.id)"
    total = conn.execute(f"SELECT COUNT(*) c FROM companies c WHERE {filtro}").fetchone()["c"]
    rows = conn.execute(f"""
        SELECT c.id, c.nombre, c.zona, c.rubro, c.sueldo_ref_min, c.sueldo_ref_max, c.sueldo_ref_confianza,
               (SELECT url FROM sources WHERE company_id=c.id ORDER BY id LIMIT 1) as fuente
        FROM companies c WHERE {filtro} ORDER BY c.id DESC LIMIT 50
    """).fetchall()
    conn.close()
    items = []
    for r in rows:
        d = dict(r)
        if d["sueldo_ref_min"] is not None:
            d["sueldo"] = f"${d['sueldo_ref_min']:,}-${d['sueldo_ref_max']:,}".replace(",", ".")
        else:
            d["sueldo"] = "No estimable"
        items.append(d)
    return jsonify({"total": total, "items": items})


@app.route("/api/company/<int:company_id>")
def api_company(company_id):
    from app.company import get_company
    return jsonify(get_company(company_id))


def run():
    init_db()
    # arranca el modo automático (cada 1 hora) solo al abrir la app, sin apretar
    # ningún botón — pensado para durar semanas con el presupuesto de por vida,
    # no para gastarlo todo en una sola sesión larga.
    scheduler.iniciar()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()
