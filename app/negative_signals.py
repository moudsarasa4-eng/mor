"""Negative Signal Engine — clasifica señales negativas por gravedad y vigencia,
y decide si descartan a la empresa automáticamente.
"""
from dataclasses import dataclass

GRAVEDAD_PUNTOS = {"baja": 5, "media": 20, "critica": 100}
VIGENCIA_MULT = {"baja": 0.3, "reciente": 0.7, "actual": 1.0}

TIPOS_CONOCIDOS = {
    "despidos", "cierre", "crisis", "concurso", "quiebra", "paro",
    "conflicto", "reduccion", "vacaciones_anticipadas", "suspensiones",
    "achique", "venta", "cierre_planta",
}


@dataclass
class NegativeSignal:
    tipo: str
    gravedad: str       # "baja" | "media" | "critica"
    vigencia: str        # "baja" | "reciente" | "actual"
    descripcion: str
    fuente_url: str
    fecha_evento: str | None = None

    def impacto(self) -> float:
        return GRAVEDAD_PUNTOS[self.gravedad] * VIGENCIA_MULT[self.vigencia]

    def descarta_automaticamente(self) -> bool:
        return self.gravedad == "critica" and self.vigencia in ("actual", "reciente")


def impacto_total(neg_signals: list[NegativeSignal]) -> float:
    return sum(s.impacto() for s in neg_signals)


def debe_descartar(neg_signals: list[NegativeSignal]) -> tuple[bool, str | None]:
    for s in neg_signals:
        if s.descarta_automaticamente():
            return True, f"{s.tipo} ({s.gravedad}, vigencia {s.vigencia}): {s.descripcion}"
    if impacto_total(neg_signals) >= 40:
        return True, "Acumulación de señales negativas supera el umbral (>=40 puntos de impacto)."
    return False, None
