"""Dashboard de terminal — salida simple (regla: la complejidad queda atrás,
la salida final se lee en 10 segundos) + detalle avanzado por empresa."""
from app.db import get_conn

RUBROS_LEGIBLES = {
    "limpieza": "Limpieza", "administrativo": "Administración",
    "atencion_cliente": "Atención al cliente", "logistica": "Logística",
}


def _fmt_sueldo(row) -> str:
    if row["sueldo_min"] is None or row["sueldo_max"] is None:
        return "No estimable"
    prefijo = "" if not row["sueldo_es_estimado"] else ""
    return f"${row['sueldo_min']:,.0f}–${row['sueldo_max']:,.0f}".replace(",", ".")


def _fmt_chances(row) -> str:
    txt = f"{row['chances_estimadas']}%"
    return f"~{txt}" if row["chances_baja_confianza"] else txt


def _nivel(jackpot_score: int) -> str:
    if jackpot_score >= 90:
        return "🟣"
    if jackpot_score >= 80:
        return "🟢"
    if jackpot_score >= 65:
        return "🟡"
    return ""


def top_oportunidades(limit: int = 10):
    """Tabla principal: solo empresas jackpot / en_revision, ordenadas por chances."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT c.id, c.nombre, c.zona, c.rubro, c.estado,
               s.jackpot_score, s.chances_estimadas, s.chances_baja_confianza,
               s.sueldo_min, s.sueldo_max, s.sueldo_es_estimado, s.puesto_objetivo,
               s.employer_score
        FROM companies c
        JOIN scores s ON s.id = (SELECT id FROM scores WHERE company_id = c.id ORDER BY creado_en DESC LIMIT 1)
        WHERE c.estado IN ('jackpot', 'en_revision')
        ORDER BY s.chances_estimadas DESC, s.employer_score DESC
        LIMIT ?
    """, (limit,)).fetchall()

    total = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    jackpots = conn.execute("SELECT COUNT(*) c FROM companies WHERE estado='jackpot'").fetchone()["c"]
    descartadas = conn.execute("SELECT COUNT(*) c FROM companies WHERE estado='descartada'").fetchone()["c"]
    conn.close()

    if not rows:
        print("Todavía no hay oportunidades cargadas.")
        return

    print("## 🏆 TOP OPORTUNIDADES\n")
    print("| Empresa | Ubicación | Rubro | Puesto al que aspiro | Chances | Sueldo estimado |")
    print("| --- | --- | --- | --- | ---: | ---: |")
    alertas = []
    for r in rows:
        nivel = _nivel(r["jackpot_score"])
        nombre = f"{nivel} {r['nombre']}".strip()
        puesto = r["puesto_objetivo"] or "(sin puesto objetivo cargado)"
        print(f"| {nombre} | {r['zona']} | {RUBROS_LEGIBLES.get(r['rubro'], r['rubro'])} | {puesto} | {_fmt_chances(r)} | {_fmt_sueldo(r)} |")
        if r["chances_baja_confianza"]:
            alertas.append(f"⚠️ {r['nombre']}: estimación de chances con evidencia limitada.")
        if r["sueldo_min"] is None:
            alertas.append(f"⚠️ {r['nombre']}: sueldo no estimable por falta de evidencia.")

    print(f"\n**{total} empresas investigadas · {jackpots} JACKPOTS · {descartadas} descartadas**\n")

    medallas = ["🥇 Prioridad", "🥈 Segunda opción", "🥉 Tercera opción"]
    for i, r in enumerate(rows[:3]):
        print(f"### {medallas[i]}\n{r['nombre']}\n")

    if alertas:
        print("\n".join(alertas))


def resumen():
    top_oportunidades()


def detalle(company_id: int):
    """Modo avanzado: toda la investigación completa detrás de la tabla."""
    from app.company import get_company
    c = get_company(company_id)
    print(f"\n{c['nombre']}")
    print(f"├── Ubicación: {c['zona']} ({c['localidad'] or 'localidad no especificada'})")
    print(f"├── Rubro: {c['rubro']}")
    if c["scores"]:
        s = c["scores"][0]
        print(f"├── Jackpot Score: {s['jackpot_score']}/100 (confianza {s['confidence']}%)")
        print(f"├── Chances de entrar: {s['chances_estimadas']}%" + (" (baja confianza)" if s["chances_baja_confianza"] else ""))
        print(f"├── CV recomendado: {s['cv_recomendado']}")
        print(f"├── Puesto objetivo: {s['puesto_objetivo'] or 'no cargado'}")
        sueldo = "No estimable" if s["sueldo_min"] is None else f"${s['sueldo_min']:,}–${s['sueldo_max']:,} (estimado)"
        print(f"├── Sueldo: {sueldo}")
    print("├── Señales de contratación:")
    for sig in c["signals"]:
        print(f"│     - [{sig['fuerza']}] {sig['tipo']}: {sig['descripcion']}")
    print("├── Señales negativas:")
    for neg in c["negative_signals"]:
        print(f"│     - [{neg['gravedad']}/{neg['vigencia']}] {neg['tipo']}: {neg['descripcion']}")
    print("├── Puestos inferidos:")
    for jh in c["job_hypotheses"]:
        print(f"│     - {jh['puesto']} ({jh['probabilidad']}%): {jh['justificacion']}")
    print("├── CV matches:")
    for m in c["cv_matches"]:
        print(f"│     - {m['cv']}: {m['match_score']}/100 — {m['justificacion']}")
    print("├── Contactos:")
    for ct in c["contacts"]:
        verif = "verificado" if ct["verificado"] else "sin verificar"
        print(f"│     - {ct['tipo']}: {ct['valor']} ({verif})")
    print("├── Fuentes:")
    for src in c["sources"]:
        print(f"│     - {src['url']}")
    print(f"└── Estado: {c['estado']}" + (f" — {c['motivo_descarte']}" if c["motivo_descarte"] else ""))


if __name__ == "__main__":
    resumen()
