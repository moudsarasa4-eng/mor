"""Outreach Writer — Generador de cuerpo de mail inteligente.

Recibe una empresa ya auditada (Company DNA) + el CV asignado, y devuelve un
email corto, específico y honesto. Nunca inventa datos: toda experiencia y
certificación sale de app/cv_data.py (fuente única = texto real de los CVs).

Niveles de certeza sobre el puesto (nunca se mezclan):
    CONFIRMADA  -> "Quisiera postularme para..."             (vacante publicada real)
    INFERIDA    -> "Quisiera ser tenido en cuenta para futuras búsquedas..."
    SIN_EVIDENCIA -> "Quisiera acercarles mi CV para futuras oportunidades..."
"""
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from app.db import get_conn, now
from app.cv_data import CANDIDATO, CVS, experiencia_relevante, certificacion_relevante

BASE_DIR = Path(__file__).resolve().parent.parent
OUTREACH_DIR = BASE_DIR / "outreach"

RUBROS_LEGIBLES = {
    "limpieza": "limpieza",
    "administrativo": "tareas administrativas",
    "atencion_cliente": "atención al cliente",
    "logistica": "logística y depósito",
}

# 5. Personalization engine: prioridad de necesidades por tipo de empresa
PRIORIDAD_POR_TIPO_EMPRESA = {
    "fabrica": ["deposito", "expedicion", "carga_descarga", "mantenimiento", "administracion"],
    "distribuidora": ["deposito", "expedicion", "recepcion", "stock", "administracion"],
    "sanatorio": ["limpieza", "desinfeccion", "administracion"],
    "clinica": ["limpieza", "desinfeccion", "administracion"],
    "supermercado": ["atencion_publico", "caja", "stock", "deposito"],
    "retail": ["atencion_publico", "caja", "stock"],
    "estudio": ["administracion", "atencion_publico", "caja"],
    "comercio": ["atencion_publico", "caja", "stock"],
}

FRASES_PROHIBIDAS_IA = [
    "me encuentro altamente interesado", "sería un honor", "mi perfil se alinea perfectamente",
    "considero que puedo aportar un gran valor", "sinergias", "dinámico y proactivo",
    "me apasiona", "me encantaría formar parte de su prestigiosa empresa",
    "prestigiosa y reconocida", "admiro profundamente la trayectoria",
    "espero ansiosamente su respuesta", "estimados señores de recursos humanos",
]


@dataclass
class OpportunityInput:
    hypothesized_role: str
    role_category: str  # cv key: limpieza | administrativo | atencion_cliente | logistica
    reasoning: str
    confidence: int  # 0-100
    nivel_evidencia: str = "SIN_EVIDENCIA"  # CONFIRMADA | INFERIDA | SIN_EVIDENCIA


@dataclass
class CompanyInput:
    name: str
    industry: str          # rubro legible, ej "distribución mayorista"
    location: str
    tipo_empresa: str = ""  # una de PRIORIDAD_POR_TIPO_EMPRESA, o "" si no aplica
    verified_facts: list[str] = field(default_factory=list)
    growth_signals: list[str] = field(default_factory=list)
    contact_email: str = ""
    contact_source: str = ""


@dataclass
class OutreachRequest:
    company: CompanyInput
    opportunity: OpportunityInput
    reason_to_contact: str  # el "por qué esta empresa" en 1 frase, para WHY_THIS_COMPANY
    mode: str = "DRAFT_MODE"  # DRAFT_MODE | SEND_MODE


@dataclass
class AuditResult:
    passed: bool
    warnings: list[str] = field(default_factory=list)


def humanization_audit(texto: str) -> list[str]:
    hallazgos = []
    texto_l = texto.lower()
    for frase in FRASES_PROHIBIDAS_IA:
        if frase in texto_l:
            hallazgos.append(f"Frase de IA-speak detectada: '{frase}'")
    return hallazgos


def _saludo() -> str:
    return "Buen día,"


def _identificacion(location: str) -> str:
    return f"Mi nombre es Marco Ammazzalorso, soy de {location} y quería acercarles mi CV para ser tenido en cuenta ante futuras oportunidades."


def _necesidades_empresa(tipo_empresa: str) -> set[str]:
    return set(PRIORIDAD_POR_TIPO_EMPRESA.get(tipo_empresa, []))


def _frase_motivo(cv: str, necesidades: set[str], nivel_evidencia: str) -> str:
    exp = experiencia_relevante(cv, necesidades, max_items=2)
    exp_txt = " y ".join(exp) if len(exp) <= 2 else ", ".join(exp[:-1]) + f" y {exp[-1]}"
    # limpiar menciones de "(Arcos Dorados)" / "(comercio mayorista)" para que suene natural
    exp_txt = re.sub(r"\s*\([^)]*\)", "", exp_txt)

    if nivel_evidencia == "CONFIRMADA":
        base = f"Quisiera postularme para el puesto, ya que cuento con experiencia en {exp_txt}."
    elif nivel_evidencia == "INFERIDA":
        base = f"Me interesó contactarlos porque cuento con experiencia en {exp_txt}, y creo que podría ser útil ante futuras búsquedas."
    else:
        base = f"Quisiera acercarles mi CV para futuras oportunidades, ya que cuento con experiencia en {exp_txt}."

    cert = certificacion_relevante(cv, necesidades)
    if cert:
        nombre_cert = cert.split(" (")[0]
        base += f" Además, cuento con formación en {nombre_cert}."
    return base


def _cierre(mode: str) -> str:
    if mode == "SEND_MODE":
        return "Adjunto mi CV para su consideración. Quedo a disposición para coordinar una entrevista."
    return "Quedo a disposición para enviarles el CV completo y coordinar una entrevista."


def generar_asunto(cv: str, opportunity: OpportunityInput) -> str:
    if opportunity.nivel_evidencia == "CONFIRMADA":
        return f"Postulación – {opportunity.hypothesized_role}"
    rubro = RUBROS_LEGIBLES[cv].capitalize()
    return f"CV para futuras oportunidades – {rubro}"


def audit_before_generate(req: OutreachRequest) -> AuditResult:
    warnings = []
    cv = req.opportunity.role_category
    if cv not in CVS:
        return AuditResult(False, [f"CV '{cv}' no existe."])
    if not req.company.name.strip():
        return AuditResult(False, ["Falta nombre de empresa."])
    if not req.company.location.strip():
        return AuditResult(False, ["Falta localidad."])
    if req.opportunity.nivel_evidencia not in ("CONFIRMADA", "INFERIDA", "SIN_EVIDENCIA"):
        return AuditResult(False, ["Nivel de evidencia inválido."])
    if req.opportunity.nivel_evidencia == "CONFIRMADA" and not req.company.verified_facts:
        warnings.append("Se afirma vacante CONFIRMADA sin verified_facts que la respalden.")
    if not req.reason_to_contact.strip():
        return AuditResult(False, ["Falta reason_to_contact (WHY_THIS_COMPANY)."])
    return AuditResult(len([w for w in warnings]) == 0 or True, warnings)  # warnings no bloquean, solo avisan


def generar_email(req: OutreachRequest) -> dict:
    """Devuelve el output estructurado: subject, email_body, audit, etc."""
    audit = audit_before_generate(req)
    cv = req.opportunity.role_category
    necesidades = _necesidades_empresa(req.company.tipo_empresa)

    cuerpo = "\n\n".join([
        _saludo(),
        _identificacion(req.company.location),
        _frase_motivo(cv, necesidades, req.opportunity.nivel_evidencia),
        _cierre(req.mode),
        "Muchas gracias por su tiempo.\n\nSaludos,\nMarco Ammazzalorso",
    ])

    palabras = len(cuerpo.split())
    warnings = list(audit.warnings)
    if palabras > 130:
        warnings.append(f"Email supera longitud recomendada ({palabras} palabras).")
    warnings.extend(humanization_audit(cuerpo))

    subject = generar_asunto(cv, req.opportunity)

    return {
        "company": req.company.name,
        "recipient": req.company.contact_email,
        "subject": subject,
        "cv_used": cv,
        "personalization_reason": req.reason_to_contact,
        "email_body": cuerpo,
        "attachment": f"cv_{cv}.pdf",
        "jackpot_score": None,  # lo completa el llamador si lo tiene
        "confidence": req.opportunity.confidence,
        "audit": {"passed": audit.passed and not any("Frase de IA-speak" in w for w in warnings), "warnings": warnings},
    }


def slug(texto: str) -> str:
    texto = texto.strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def guardar_outreach(company_id: int, req: OutreachRequest, resultado: dict,
                      jackpot_score: int | None = None,
                      evidencias_fuentes: list[str] | None = None) -> str:
    if not resultado["audit"]["passed"]:
        raise ValueError(f"No se genera el archivo: auditoría no pasó. Warnings: {resultado['audit']['warnings']}")

    hoy = date.today().isoformat()
    OUTREACH_DIR.mkdir(exist_ok=True)
    archivo = OUTREACH_DIR / f"{hoy}_{slug(req.company.name)}_{req.opportunity.role_category}.md"

    fuentes_txt = "\n".join(f"- {f}" for f in (evidencias_fuentes or [])) or "- (sin fuentes registradas)"

    contenido = f"""# {req.company.name}

## Jackpot Score
{jackpot_score if jackpot_score is not None else "N/D"}/100

## CV utilizado
{resultado['cv_used']}

## Puesto objetivo
{req.opportunity.hypothesized_role} ({req.opportunity.nivel_evidencia})

## Motivo de selección
{req.reason_to_contact}

## Evidencias utilizadas
{fuentes_txt}

## Contacto
{req.company.contact_email or "sin contacto verificado"}

## Asunto
{resultado['subject']}

## Cuerpo del email

```
Asunto: {resultado['subject']}

{resultado['email_body']}
```

## Auditoría
{"PASS" if resultado['audit']['passed'] else "FAIL"}
{chr(10).join('- ' + w for w in resultado['audit']['warnings'])}

## Estado
PENDIENTE DE REVISIÓN HUMANA
"""
    archivo.write_text(contenido, encoding="utf-8")

    conn = get_conn()
    conn.execute(
        "INSERT INTO outreach (company_id, cv_usado, why_this_company, email_texto, archivo_md, estado, creado_en, actualizado_en) "
        "VALUES (?, ?, ?, ?, ?, 'generado', ?, ?)",
        (company_id, resultado["cv_used"], req.reason_to_contact, resultado["email_body"], str(archivo), now(), now()),
    )
    conn.commit()
    conn.close()

    return str(archivo)


def actualizar_estado_outreach(outreach_id: int, nuevo_estado: str):
    """nuevo_estado en: generado, enviado, respondio, entrevista, rechazo, no_respondio, contratacion"""
    conn = get_conn()
    conn.execute("UPDATE outreach SET estado=?, actualizado_en=? WHERE id=?", (nuevo_estado, now(), outreach_id))
    conn.commit()
    conn.close()
