#!/usr/bin/env python3
"""Motor de Jackpots — CLI unificado.

Subcomandos:
    init-db
    add-company            registra/actualiza una empresa (Company DNA)
    add-signal / add-negative-signal / add-hypothesis / add-cv-match / add-contact / add-source
    score                  recalcula employer/hiring/jackpot score y confidence
    audit                  corre el checklist antes de outreach
    outreach                genera el email (requiere auditoría aprobada)
    why-not                 explica por qué se descartó una empresa
    dashboard / detalle
    siguiente-zona / marcar-zona
    learning                 analiza resultados de outreach reales

No busca en internet ni envía nada: es la capa de datos, scoring y generación.
La investigación (descubrimiento, verificación, lectura de fuentes) la hace
Claude junto al usuario, zona por zona, y carga los resultados acá.
"""
import argparse
import json
import sys

from app.db import init_db, get_conn, now
from app.company import (
    upsert_company, add_source, add_signal, add_negative_signal,
    add_job_hypothesis, add_cv_match, add_contact, get_company,
    calcular_y_guardar_score, why_not, add_transport_access,
)
from app.signals import Signal
from app.negative_signals import NegativeSignal
from app.scoring import EmployerInputs, Evidencia
from app.audit import AuditChecklist, auditar
from app.outreach import OutreachRequest, CompanyInput, OpportunityInput, generar_email, guardar_outreach
from app.geography import accessibility_score, LINEA_SAN_MARTIN
import yaml
from pathlib import Path

CONFIG = yaml.safe_load((Path(__file__).resolve().parent / "config.yaml").read_text(encoding="utf-8"))


def cmd_init_db(args):
    init_db()
    print("Base de datos inicializada.")


def cmd_add_company(args):
    cid = upsert_company(args.nombre, args.rubro, args.zona, args.localidad or "",
                          args.antiguedad, args.tamano, args.actividad or "")
    print(f"Empresa registrada/actualizada. id={cid}")


def cmd_add_source(args):
    sid = add_source(args.company_id, args.url, args.tipo, args.descripcion or "")
    print(f"Fuente registrada. id={sid}")


def cmd_add_signal(args):
    sig = Signal(tipo=args.tipo, fuerza=args.fuerza, descripcion=args.descripcion, fuente_url="", fecha_evento=args.fecha)
    add_signal(args.company_id, sig, args.fuente_id)
    print("Señal de contratación registrada.")


def cmd_add_negative_signal(args):
    neg = NegativeSignal(tipo=args.tipo, gravedad=args.gravedad, vigencia=args.vigencia,
                          descripcion=args.descripcion, fuente_url="", fecha_evento=args.fecha)
    add_negative_signal(args.company_id, neg, args.fuente_id)
    print("Señal negativa registrada.")


def cmd_add_hypothesis(args):
    add_job_hypothesis(args.company_id, args.puesto, args.probabilidad, args.justificacion)
    print("Hipótesis de puesto registrada.")


def cmd_add_cv_match(args):
    add_cv_match(args.company_id, args.cv, args.score, args.justificacion)
    print("Match de CV registrado.")


def cmd_add_contact(args):
    add_contact(args.company_id, args.tipo, args.valor, args.verificado, args.fuente_id)
    print("Contacto registrado (a nivel empresa).")


def cmd_score(args):
    emp_inputs = EmployerInputs(
        estabilidad=args.estabilidad, tamano=args.tamano, antiguedad=args.antiguedad,
        crecimiento=args.crecimiento, formalidad=args.formalidad, actividad_actual=args.actividad_actual,
    )
    acc = accessibility_score(args.zona, tiene_otro_transporte=args.otro_transporte)
    evidencias = [Evidencia(afirmacion=e["afirmacion"], nivel=e["nivel"]) for e in json.loads(args.evidencias)] if args.evidencias else []
    resultado = calcular_y_guardar_score(
        args.company_id, emp_inputs, accessibility=acc,
        contactability=100 if args.contacto_verificado else 0, evidencias=evidencias,
        puesto_objetivo=args.puesto_objetivo, vacante_confirmada=args.vacante_confirmada,
        sueldo_min=args.sueldo_min, sueldo_max=args.sueldo_max, sueldo_fuente=args.sueldo_fuente,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


def cmd_audit(args):
    checklist = AuditChecklist(
        empresa_existe=args.empresa_existe, localidad_correcta=args.localidad_correcta,
        fuentes_independientes=args.fuentes_independientes,
        contacto_pertenece_a_empresa=args.contacto_pertenece_a_empresa,
        email_publicado_por_la_empresa=args.email_publicado,
        experiencia_verificada_en_cv=args.experiencia_verificada,
        sin_contradicciones=args.sin_contradicciones,
        sin_señales_negativas_criticas=args.sin_senales_criticas,
        inferencia_puesto_justificada=args.inferencia_justificada,
        notas=args.notas or "",
    )
    resultado, fallos = auditar(args.company_id, checklist)
    print(f"Resultado: {resultado}")
    if fallos:
        print("Fallos críticos:", ", ".join(fallos))


def cmd_outreach(args):
    conn = get_conn()
    contacto = conn.execute(
        "SELECT valor FROM contacts WHERE company_id=? AND tipo='email' AND verificado=1 LIMIT 1", (args.company_id,)
    ).fetchone()
    fuentes = [r["url"] for r in conn.execute("SELECT url FROM sources WHERE company_id=?", (args.company_id,))]
    ultimo = conn.execute(
        "SELECT jackpot_score FROM scores WHERE company_id=? ORDER BY creado_en DESC LIMIT 1", (args.company_id,)
    ).fetchone()
    conn.close()

    req = OutreachRequest(
        company=CompanyInput(
            name=args.nombre, industry=args.rubro, location=args.zona,
            tipo_empresa=args.tipo_empresa or "",
            contact_email=contacto["valor"] if contacto else "",
        ),
        opportunity=OpportunityInput(
            hypothesized_role=args.puesto, role_category=args.cv,
            reasoning=args.why, confidence=args.confianza,
            nivel_evidencia=args.nivel_evidencia,
        ),
        reason_to_contact=args.why,
        mode=args.modo,
    )
    resultado = generar_email(req)
    if not resultado["audit"]["passed"]:
        print("NO GENERADO. Auditoría falló:", resultado["audit"]["warnings"])
        return
    archivo = guardar_outreach(args.company_id, req, resultado,
                                jackpot_score=ultimo["jackpot_score"] if ultimo else None,
                                evidencias_fuentes=fuentes)
    print(f"Generado: {archivo}")
    if resultado["audit"]["warnings"]:
        print("Avisos:", resultado["audit"]["warnings"])


def cmd_why_not(args):
    r = why_not(args.company_id)
    print(r or "La empresa no está descartada (o no tiene motivo registrado).")


def cmd_dashboard(args):
    from app.dashboard import top_oportunidades
    top_oportunidades(limit=args.limit)


def cmd_detalle(args):
    from app.dashboard import detalle
    detalle(args.company_id)


def cmd_siguiente_zona(args):
    conn = get_conn()
    auditadas = {r["zona"] for r in conn.execute("SELECT DISTINCT zona FROM runs")}
    conn.close()
    orden = CONFIG["zonas"]["cercana"] + CONFIG["zonas"]["media"] + CONFIG["zonas"]["extendida"]
    for z in orden:
        if z not in auditadas:
            print(z)
            return
    print("Todas las zonas fueron auditadas.")


def cmd_marcar_zona(args):
    conn = get_conn()
    evaluadas = conn.execute("SELECT COUNT(*) c FROM companies WHERE zona=?", (args.zona,)).fetchone()["c"]
    jackpots = conn.execute("SELECT COUNT(*) c FROM companies WHERE zona=? AND estado='jackpot'", (args.zona,)).fetchone()["c"]
    descartadas = conn.execute("SELECT COUNT(*) c FROM companies WHERE zona=? AND estado='descartada'", (args.zona,)).fetchone()["c"]
    conn.execute(
        "INSERT INTO runs (zona, empresas_evaluadas, jackpots, descartadas, creado_en) VALUES (?, ?, ?, ?, ?)",
        (args.zona, evaluadas, jackpots, descartadas, now()),
    )
    conn.commit()
    conn.close()
    print(f"Zona '{args.zona}' marcada. Evaluadas={evaluadas} Jackpots={jackpots} Descartadas={descartadas}")


def cmd_learning(args):
    from app.learning import analizar_resultados
    print(json.dumps(analizar_resultados(), ensure_ascii=False, indent=2))


def cmd_feedback(args):
    from app.feedback import marcar
    marcar(args.company_id, args.marca, args.nota or "")
    print("Feedback registrado.")


def cmd_discard_reason(args):
    from app.feedback import registrar_descarte
    registrar_descarte(args.company_id, args.codigo, args.detalle or "", args.reintentar_despues)
    print("Motivo de descarte registrado.")


def cmd_learning_report(args):
    from app.learning_report import generar_reporte
    print(f"Generado: {generar_reporte()}")


def cmd_add_transport(args):
    add_transport_access(args.company_id, args.red, args.tipo, args.minutos_caminata,
                          args.minutos_viaje_total, args.combinaciones, args.fuente or "")
    print("Acceso de transporte registrado.")


def main():
    p = argparse.ArgumentParser(description="Motor de Jackpots")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db").set_defaults(func=cmd_init_db)

    pc = sub.add_parser("add-company")
    pc.add_argument("--nombre", required=True)
    pc.add_argument("--rubro", required=True, choices=["limpieza", "administrativo", "atencion_cliente", "logistica"])
    pc.add_argument("--zona", required=True)
    pc.add_argument("--localidad", default="")
    pc.add_argument("--antiguedad", type=int, default=None)
    pc.add_argument("--tamano", default="desconocido", choices=["chica", "mediana", "grande", "desconocido"])
    pc.add_argument("--actividad", default="")
    pc.set_defaults(func=cmd_add_company)

    ps = sub.add_parser("add-source")
    ps.add_argument("--company-id", type=int, required=True, dest="company_id")
    ps.add_argument("--url", required=True)
    ps.add_argument("--tipo", default="otro", choices=["sitio_propio", "directorio", "noticia", "otro"])
    ps.add_argument("--descripcion", default="")
    ps.set_defaults(func=cmd_add_source)

    psi = sub.add_parser("add-signal")
    psi.add_argument("--company-id", type=int, required=True, dest="company_id")
    psi.add_argument("--tipo", required=True)
    psi.add_argument("--fuerza", required=True, choices=["fuerte", "media", "debil"])
    psi.add_argument("--descripcion", required=True)
    psi.add_argument("--fecha", default=None)
    psi.add_argument("--fuente-id", type=int, default=None, dest="fuente_id")
    psi.set_defaults(func=cmd_add_signal)

    pn = sub.add_parser("add-negative-signal")
    pn.add_argument("--company-id", type=int, required=True, dest="company_id")
    pn.add_argument("--tipo", required=True)
    pn.add_argument("--gravedad", required=True, choices=["baja", "media", "critica"])
    pn.add_argument("--vigencia", required=True, choices=["baja", "reciente", "actual"])
    pn.add_argument("--descripcion", required=True)
    pn.add_argument("--fecha", default=None)
    pn.add_argument("--fuente-id", type=int, default=None, dest="fuente_id")
    pn.set_defaults(func=cmd_add_negative_signal)

    ph = sub.add_parser("add-hypothesis")
    ph.add_argument("--company-id", type=int, required=True, dest="company_id")
    ph.add_argument("--puesto", required=True)
    ph.add_argument("--probabilidad", type=int, required=True)
    ph.add_argument("--justificacion", required=True)
    ph.set_defaults(func=cmd_add_hypothesis)

    pm = sub.add_parser("add-cv-match")
    pm.add_argument("--company-id", type=int, required=True, dest="company_id")
    pm.add_argument("--cv", required=True, choices=["limpieza", "administrativo", "atencion_cliente", "logistica"])
    pm.add_argument("--score", type=int, required=True)
    pm.add_argument("--justificacion", required=True)
    pm.set_defaults(func=cmd_add_cv_match)

    pco = sub.add_parser("add-contact")
    pco.add_argument("--company-id", type=int, required=True, dest="company_id")
    pco.add_argument("--tipo", required=True, choices=["email", "telefono", "formulario"])
    pco.add_argument("--valor", required=True)
    pco.add_argument("--verificado", action="store_true")
    pco.add_argument("--fuente-id", type=int, default=None, dest="fuente_id")
    pco.set_defaults(func=cmd_add_contact)

    psc = sub.add_parser("score")
    psc.add_argument("--company-id", type=int, required=True, dest="company_id")
    psc.add_argument("--zona", required=True)
    psc.add_argument("--estabilidad", type=int, required=True)
    psc.add_argument("--tamano", type=int, required=True)
    psc.add_argument("--antiguedad", type=int, required=True)
    psc.add_argument("--crecimiento", type=int, required=True)
    psc.add_argument("--formalidad", type=int, required=True)
    psc.add_argument("--actividad-actual", type=int, required=True, dest="actividad_actual")
    psc.add_argument("--otro-transporte", action="store_true", dest="otro_transporte")
    psc.add_argument("--contacto-verificado", action="store_true", dest="contacto_verificado")
    psc.add_argument("--evidencias", default=None, help='JSON: [{"afirmacion": "...", "nivel": "OBSERVADO"}]')
    psc.add_argument("--puesto-objetivo", default=None, dest="puesto_objetivo")
    psc.add_argument("--vacante-confirmada", action="store_true", dest="vacante_confirmada")
    psc.add_argument("--sueldo-min", type=int, default=None, dest="sueldo_min")
    psc.add_argument("--sueldo-max", type=int, default=None, dest="sueldo_max")
    psc.add_argument("--sueldo-fuente", default=None, dest="sueldo_fuente")
    psc.set_defaults(func=cmd_score)

    pa = sub.add_parser("audit")
    pa.add_argument("--company-id", type=int, required=True, dest="company_id")
    pa.add_argument("--empresa-existe", action="store_true", dest="empresa_existe")
    pa.add_argument("--localidad-correcta", action="store_true", dest="localidad_correcta")
    pa.add_argument("--fuentes-independientes", action="store_true", dest="fuentes_independientes")
    pa.add_argument("--contacto-pertenece-a-empresa", action="store_true", dest="contacto_pertenece_a_empresa")
    pa.add_argument("--email-publicado", action="store_true", dest="email_publicado")
    pa.add_argument("--experiencia-verificada", action="store_true", dest="experiencia_verificada")
    pa.add_argument("--sin-contradicciones", action="store_true", dest="sin_contradicciones")
    pa.add_argument("--sin-senales-criticas", action="store_true", dest="sin_senales_criticas")
    pa.add_argument("--inferencia-justificada", action="store_true", dest="inferencia_justificada")
    pa.add_argument("--notas", default="")
    pa.set_defaults(func=cmd_audit)

    po = sub.add_parser("outreach")
    po.add_argument("--company-id", type=int, required=True, dest="company_id")
    po.add_argument("--nombre", required=True)
    po.add_argument("--rubro", required=True, choices=["limpieza", "administrativo", "atencion_cliente", "logistica"])
    po.add_argument("--zona", required=True)
    po.add_argument("--tipo-empresa", default="", dest="tipo_empresa",
                     choices=["", "fabrica", "distribuidora", "sanatorio", "clinica", "supermercado", "retail", "estudio", "comercio"])
    po.add_argument("--cv", required=True, choices=["limpieza", "administrativo", "atencion_cliente", "logistica"])
    po.add_argument("--puesto", required=True, help="Puesto hipotético, ej 'Operario de depósito'")
    po.add_argument("--why", required=True, help="Explicación WHY_THIS_COMPANY / motivo de contacto")
    po.add_argument("--confianza", type=int, default=50)
    po.add_argument("--nivel-evidencia", default="SIN_EVIDENCIA", dest="nivel_evidencia",
                     choices=["CONFIRMADA", "INFERIDA", "SIN_EVIDENCIA"])
    po.add_argument("--modo", default="DRAFT_MODE", choices=["DRAFT_MODE", "SEND_MODE"])
    po.set_defaults(func=cmd_outreach)

    pwn = sub.add_parser("why-not")
    pwn.add_argument("--company-id", type=int, required=True, dest="company_id")
    pwn.set_defaults(func=cmd_why_not)

    pdash = sub.add_parser("dashboard")
    pdash.add_argument("--limit", type=int, default=10)
    pdash.set_defaults(func=cmd_dashboard)

    pd = sub.add_parser("detalle")
    pd.add_argument("--company-id", type=int, required=True, dest="company_id")
    pd.set_defaults(func=cmd_detalle)

    sub.add_parser("siguiente-zona").set_defaults(func=cmd_siguiente_zona)

    pmz = sub.add_parser("marcar-zona")
    pmz.add_argument("zona")
    pmz.set_defaults(func=cmd_marcar_zona)

    sub.add_parser("learning").set_defaults(func=cmd_learning)

    pf = sub.add_parser("feedback")
    pf.add_argument("--company-id", type=int, required=True, dest="company_id")
    pf.add_argument("--marca", required=True, choices=["EXCELENTE", "BUEN_JACKPOT", "MALA_EMPRESA", "FALSO_POSITIVO", "PRIORITARIA", "NO_BUSCAR_DE_NUEVO"])
    pf.add_argument("--nota", default="")
    pf.set_defaults(func=cmd_feedback)

    pdr = sub.add_parser("discard-reason")
    pdr.add_argument("--company-id", type=int, required=True, dest="company_id")
    pdr.add_argument("--codigo", required=True, choices=["NO_CONTACT", "HOMONYM", "NEGATIVE_SIGNAL", "TOO_SMALL",
                      "LOW_STABILITY", "LOW_CV_MATCH", "NO_RELEVANT_OPERATION", "NO_VERIFIABLE_CONTACT",
                      "OUTDATED_INFORMATION", "DUPLICATE", "LOW_OPPORTUNITY"])
    pdr.add_argument("--detalle", default="")
    pdr.add_argument("--reintentar-despues", default=None, dest="reintentar_despues")
    pdr.set_defaults(func=cmd_discard_reason)

    sub.add_parser("learning-report").set_defaults(func=cmd_learning_report)

    pt = sub.add_parser("add-transport")
    pt.add_argument("--company-id", type=int, required=True, dest="company_id")
    pt.add_argument("--red", required=True, help='"San Martín" | "182" | "320" | "237" | "463" | otra')
    pt.add_argument("--tipo", required=True, choices=["tren", "colectivo"])
    pt.add_argument("--minutos-caminata", type=int, required=True, dest="minutos_caminata")
    pt.add_argument("--minutos-viaje-total", type=int, required=True, dest="minutos_viaje_total")
    pt.add_argument("--combinaciones", type=int, default=0)
    pt.add_argument("--fuente", default="", help="cómo se estimó, ej 'mapa'")
    pt.set_defaults(func=cmd_add_transport)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
