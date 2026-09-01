"""Dashboard de terminal — resumen general y detalle por empresa."""
from app.db import get_conn


def resumen():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    por_estado = {r["estado"]: r["c"] for r in conn.execute(
        "SELECT estado, COUNT(*) c FROM companies GROUP BY estado"
    )}
    top = conn.execute("""
        SELECT c.nombre, c.rubro, s.jackpot_score
        FROM companies c
        JOIN scores s ON s.id = (
            SELECT id FROM scores WHERE company_id = c.id ORDER BY creado_en DESC LIMIT 1
        )
        WHERE c.estado = 'jackpot'
        ORDER BY s.jackpot_score DESC
        LIMIT 10
    """).fetchall()
    conn.close()

    print("╔══════════════════════════════════════════════╗")
    print("║        MOTOR DE JACKPOTS                     ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║ Empresas analizadas             {total:<13}║")
    print(f"║ Jackpot                         {por_estado.get('jackpot', 0):<13}║")
    print(f"║ En revisión                     {por_estado.get('en_revision', 0):<13}║")
    print(f"║ Descartadas                     {por_estado.get('descartada', 0):<13}║")
    print("║                                                ║")
    print("║ 🟣 TOP JACKPOTS                               ║")
    print("║                                                ║")
    for row in top:
        linea = f"{row['nombre'][:16]:<16} {row['jackpot_score']}/100    {row['rubro'].upper()}"
        print(f"║ {linea:<46} ║")
    print("╚══════════════════════════════════════════════╝")


def detalle(company_id: int):
    from app.company import get_company
    c = get_company(company_id)
    print(f"\n{c['nombre']}")
    print(f"├── Ubicación: {c['zona']} ({c['localidad'] or 'localidad no especificada'})")
    print(f"├── Rubro: {c['rubro']}")
    if c["scores"]:
        s = c["scores"][0]
        print(f"├── Score: {s['jackpot_score']}/100 (confianza {s['confidence']}%)")
        print(f"├── CV recomendado: {s['cv_recomendado']}")
    print("├── Señales de contratación:")
    for sig in c["signals"]:
        print(f"│     - [{sig['fuerza']}] {sig['tipo']}: {sig['descripcion']}")
    print("├── Señales negativas:")
    for neg in c["negative_signals"]:
        print(f"│     - [{neg['gravedad']}/{neg['vigencia']}] {neg['tipo']}: {neg['descripcion']}")
    print("├── Puestos inferidos:")
    for jh in c["job_hypotheses"]:
        print(f"│     - {jh['puesto']} ({jh['probabilidad']}%): {jh['justificacion']}")
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
