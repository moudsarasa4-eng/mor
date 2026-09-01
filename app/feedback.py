"""Feedback humano — marcas manuales del usuario sobre una empresa, con peso alto
en el aprendizaje (se diferencia explícitamente de las señales automáticas)."""
from app.db import get_conn, now

MARCAS_VALIDAS = {"EXCELENTE", "BUEN_JACKPOT", "MALA_EMPRESA", "FALSO_POSITIVO", "PRIORITARIA", "NO_BUSCAR_DE_NUEVO"}


def marcar(company_id: int, marca: str, nota: str = ""):
    if marca not in MARCAS_VALIDAS:
        raise ValueError(f"Marca inválida: {marca}. Válidas: {MARCAS_VALIDAS}")
    conn = get_conn()
    conn.execute(
        "INSERT INTO human_feedback (company_id, marca, nota, creado_en) VALUES (?, ?, ?, ?)",
        (company_id, marca, nota, now()),
    )
    if marca == "NO_BUSCAR_DE_NUEVO":
        conn.execute("UPDATE companies SET estado='descartada', motivo_descarte=? WHERE id=?",
                     (f"Feedback humano: no volver a buscar. {nota}", company_id))
    conn.commit()
    conn.close()


def registrar_descarte(company_id: int, codigo: str, detalle: str = "", reintentar_despues: str | None = None):
    """codigo: NO_CONTACT | HOMONYM | NEGATIVE_SIGNAL | TOO_SMALL | LOW_STABILITY |
    LOW_CV_MATCH | NO_RELEVANT_OPERATION | NO_VERIFIABLE_CONTACT | OUTDATED_INFORMATION |
    DUPLICATE | LOW_OPPORTUNITY"""
    conn = get_conn()
    conn.execute(
        "INSERT INTO discard_reasons (company_id, codigo, detalle, reintentar_despues, creado_en) VALUES (?, ?, ?, ?, ?)",
        (company_id, codigo, detalle, reintentar_despues, now()),
    )
    conn.commit()
    conn.close()
