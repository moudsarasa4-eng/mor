"""Job Signal Engine — clasifica señales de contratación (directas o indirectas)
y calcula el HIRING_SIGNAL_SCORE (0-100).

Este módulo NO busca en internet. Recibe señales ya detectadas (por Claude durante
la investigación de una zona) y las puntúa de forma consistente.
"""
from dataclasses import dataclass

FUERZA_PUNTOS = {
    "fuerte": 20,
    "media": 10,
    "debil": 3,
}

SEÑALES_FUERTES = {
    "nueva_planta", "nueva_sucursal", "ampliacion", "inversion",
    "aumento_produccion", "nueva_linea_productiva", "incorporacion_maquinaria",
    "expansion_logistica", "apertura_deposito", "crecimiento_operaciones",
    "nuevos_horarios", "aumento_capacidad", "contratacion_reciente_similar",
    "aumento_actividad", "mudanza_parque_industrial",
}

SEÑALES_MEDIAS = {
    "publicaciones_recientes_actividad", "crecimiento_instalaciones",
    "nuevas_unidades_negocio", "incremento_distribucion", "nuevas_sucursales",
    "cambios_operativos",
}

SEÑALES_DEBILES = {
    "empresa_grande_sin_senales", "empresa_antigua", "presencia_digital_activa",
}


@dataclass
class Signal:
    tipo: str
    fuerza: str  # "fuerte" | "media" | "debil"
    descripcion: str
    fuente_url: str
    fecha_evento: str | None = None


def clasificar_fuerza(tipo: str) -> str:
    if tipo in SEÑALES_FUERTES:
        return "fuerte"
    if tipo in SEÑALES_MEDIAS:
        return "media"
    if tipo in SEÑALES_DEBILES:
        return "debil"
    return "media"  # default conservador para señales no catalogadas


def hiring_signal_score(signals: list[Signal]) -> int:
    """Suma con rendimientos decrecientes (evita que 10 señales débiles == 1 fuerte)."""
    if not signals:
        return 0
    puntos = sorted((FUERZA_PUNTOS[s.fuerza] for s in signals), reverse=True)
    total = 0.0
    for i, p in enumerate(puntos):
        total += p * (0.6 ** i)  # cada señal adicional pesa menos
    return min(100, round(total))


def nivel(score: int) -> str:
    if score <= 20:
        return "poca evidencia"
    if score <= 40:
        return "posible"
    if score <= 60:
        return "interesante"
    if score <= 80:
        return "fuerte"
    return "JACKPOT POTENCIAL"
