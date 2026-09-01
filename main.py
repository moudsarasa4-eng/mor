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
    calcular_y_guardar_score, why_not,
)
from app.signals import Signal
from app.negative_signals import NegativeSignal
from app.scoring import EmployerInputs, Evidencia
from app.audit import AuditChecklist, auditar
from app.outreach import generar_outreach
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
    exp = Path(args.experiencia_file).read_text(encoding="utf-8")
    archivo = generar_outreach(args.company_id, args.nombre, args.rubro, args.cv, args.why, exp)
    print(f"Generado: {archivo}")


def cmd_why_not(args):
    r = why_not(args.company_id)
    print(r or "La empresa no está descartada (o no tiene motivo registrado).")


def cmd_dashboard(args):
    from app.dashboard import resumen
    resumen()


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
    po.add_argument("--cv", required=True, choices=["limpieza", "administrativo", "atencion_cliente", "logistica"])
    po.add_argument("--why", required=True, help="Explicación WHY_THIS_COMPANY")
    po.add_argument("--experiencia-file", required=True, dest="experiencia_file")
    po.set_defaults(func=cmd_outreach)

    pwn = sub.add_parser("why-not")
    pwn.add_argument("--company-id", type=int, required=True, dest="company_id")
    pwn.set_defaults(func=cmd_why_not)

    sub.add_parser("dashboard").set_defaults(func=cmd_dashboard)

    pd = sub.add_parser("detalle")
    pd.add_argument("--company-id", type=int, required=True, dest="company_id")
    pd.set_defaults(func=cmd_detalle)

    sub.add_parser("siguiente-zona").set_defaults(func=cmd_siguiente_zona)

    pmz = sub.add_parser("marcar-zona")
    pmz.add_argument("zona")
    pmz.set_defaults(func=cmd_marcar_zona)

    sub.add_parser("learning").set_defaults(func=cmd_learning)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
