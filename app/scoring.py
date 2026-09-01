"""Employer Quality Score + Jackpot Score compuesto, con nivel de confianza y
evidencia clasificada como OBSERVADO / INFERIDO / NO_DETERMINADO / REQUIERE_REVISION.
"""
from dataclasses import dataclass, field

NIVELES_EVIDENCIA = {"OBSERVADO", "INFERIDO", "NO_DETERMINADO", "REQUIERE_REVISION"}


@dataclass
class Evidencia:
    afirmacion: str
    nivel: str  # uno de NIVELES_EVIDENCIA

    def __post_init__(self):
        if self.nivel not in NIVELES_EVIDENCIA:
            raise ValueError(f"Nivel de evidencia inválido: {self.nivel}")


@dataclass
class EmployerInputs:
    estabilidad: int          # 0-100
    tamano: int                # 0-100
    antiguedad: int            # 0-100
    crecimiento: int           # 0-100
    formalidad: int            # 0-100
    actividad_actual: int      # 0-100


def employer_score(inputs: EmployerInputs) -> int:
    pesos = {
        "estabilidad": 0.20, "tamano": 0.15, "antiguedad": 0.15,
        "crecimiento": 0.20, "formalidad": 0.15, "actividad_actual": 0.15,
    }
    total = (
        inputs.estabilidad * pesos["estabilidad"]
        + inputs.tamano * pesos["tamano"]
        + inputs.antiguedad * pesos["antiguedad"]
        + inputs.crecimiento * pesos["crecimiento"]
        + inputs.formalidad * pesos["formalidad"]
        + inputs.actividad_actual * pesos["actividad_actual"]
    )
    return round(total)


@dataclass
class JackpotInputs:
    employer_quality: int      # de employer_score()
    opportunity_match: int     # del mejor CV match (cv_match.py)
    hiring_signals: int        # de signals.hiring_signal_score()
    accessibility: int         # de geography.accessibility_score()
    contactability: int        # 0 si no hay contacto verificado, 100 si sí


PESOS_JACKPOT = {
    "employer_quality": 0.25,
    "opportunity_match": 0.30,
    "hiring_signals": 0.25,
    "accessibility": 0.10,
    "contactability": 0.10,
}


def jackpot_score(inputs: JackpotInputs) -> int:
    total = sum(getattr(inputs, k) * w for k, w in PESOS_JACKPOT.items())
    return round(total)


def confidence(evidencias: list[Evidencia], tiene_contacto_verificado: bool, cantidad_fuentes_independientes: int) -> int:
    """Confianza 0-100: más fuentes independientes y más OBSERVADO (vs INFERIDO) = más confianza."""
    if not evidencias:
        base = 30
    else:
        observado = sum(1 for e in evidencias if e.nivel == "OBSERVADO")
        inferido = sum(1 for e in evidencias if e.nivel == "INFERIDO")
        no_det = sum(1 for e in evidencias if e.nivel == "NO_DETERMINADO")
        req_rev = sum(1 for e in evidencias if e.nivel == "REQUIERE_REVISION")
        total = len(evidencias)
        base = (observado * 100 + inferido * 55 - no_det * 10 - req_rev * 15) / total
        base = max(0, base)

    ajuste_fuentes = min(20, cantidad_fuentes_independientes * 5)
    ajuste_contacto = 10 if tiene_contacto_verificado else -10
    return int(max(0, min(100, base + ajuste_fuentes + ajuste_contacto)))


def chances_de_entrar(opportunity_score: int, hiring_signal_score: int, employer_score: int,
                       vacante_confirmada: bool) -> tuple[int, bool]:
    """'Chances de entrar' (regla 16): NO es lo mismo que CV match. Combina match,
    señales de contratación y calidad de empresa, con descuento si no hay vacante
    confirmada (competencia desconocida). Devuelve (chances, baja_confianza)."""
    base = opportunity_score * 0.5 + hiring_signal_score * 0.35 + employer_score * 0.15
    if not vacante_confirmada:
        base *= 0.85  # sin vacante confirmada, hay incertidumbre de que exista búsqueda activa
    chances = round(min(100, max(0, base)))
    baja_confianza = hiring_signal_score < 30 or opportunity_score < 40
    return chances, baja_confianza


def clasificar_jackpot(score: int) -> str:
    if score >= 90:
        return "🟣 JACKPOT"
    if score >= 80:
        return "🟢 MUY INTERESANTE"
    if score >= 65:
        return "🟡 INVESTIGAR"
    return "🔴 DESCARTAR"
