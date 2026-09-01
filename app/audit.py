"""Audit Agent — checklist obligatorio antes de que una empresa pase a outreach.
Si falla algún ítem crítico, el resultado es REQUIERE_REVISION, no se genera el email.
"""
from dataclasses import dataclass, field

from app.db import get_conn, now


@dataclass
class AuditChecklist:
    empresa_existe: bool
    localidad_correcta: bool          # no es homónimo de otra provincia/país
    fuentes_independientes: bool      # al menos 2 fuentes distintas
    contacto_pertenece_a_empresa: bool
    email_publicado_por_la_empresa: bool
    experiencia_verificada_en_cv: bool  # el texto de experiencia usado sale literal del CV
    sin_contradicciones: bool
    sin_señales_negativas_criticas: bool
    inferencia_puesto_justificada: bool
    notas: str = ""


CRITICOS = [
    "empresa_existe", "localidad_correcta", "contacto_pertenece_a_empresa",
    "experiencia_verificada_en_cv", "sin_señales_negativas_criticas",
]


def auditar(company_id: int, checklist: AuditChecklist) -> tuple[str, list[str]]:
    fallos = [campo for campo in CRITICOS if not getattr(checklist, campo)]
    resultado = "aprobado" if not fallos else "requiere_revision"

    conn = get_conn()
    import json
    conn.execute(
        "INSERT INTO audit_log (company_id, resultado, checklist_json, creado_en) VALUES (?, ?, ?, ?)",
        (company_id, resultado, json.dumps(checklist.__dict__, ensure_ascii=False), now()),
    )
    conn.commit()
    conn.close()
    return resultado, fallos
