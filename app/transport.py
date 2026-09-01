"""Motor de movilidad — manual-asistido (sin geocoding automático).

Durante la investigación de cada empresa, se carga a mano qué redes de transporte
prioritarias la sirven (estación/línea + minutos de caminata, verificados por vista
de mapa en ese momento). Este módulo calcula el score de accesibilidad multimodal,
la bonificación por multiacceso y arma la mejor ruta resumen para la tabla.

No incluye: geocoding automático de paradas, cálculo de rutas vía API de routing,
ni "barrido" de empresas cercanas a cada parada (eso requeriría APIs de mapas con
credenciales y, a la escala pedida originalmente, scraping masivo — fuera de
alcance de este motor curado).
"""
from dataclasses import dataclass, field

REDES_PRIORITARIAS = [
    {"tipo": "tren", "nombre": "San Martín", "prioridad": 1},
    {"tipo": "colectivo", "nombre": "182", "prioridad": 2},
    {"tipo": "colectivo", "nombre": "320", "prioridad": 3},
    {"tipo": "colectivo", "nombre": "237", "prioridad": 4},
    {"tipo": "colectivo", "nombre": "463", "prioridad": 5},
]

BONUS_POR_CANTIDAD_LINEAS = {1: 0, 2: 5, 3: 10}  # 4+ -> 15


@dataclass
class AccesoTransporte:
    red: str                  # "San Martín" | "182" | "320" | "237" | "463" | otra
    tipo: str                 # "tren" | "colectivo"
    minutos_caminata: int      # desde la empresa hasta la parada/estación, estimado a mano
    minutos_viaje_total: int   # casa -> parada -> viaje -> parada -> empresa, estimado a mano
    combinaciones: int = 0     # cantidad de transbordos
    fuente: str = ""           # cómo se estimó (ej. "mapa", "búsqueda de horarios")


def _tiempo_a_nivel(minutos: int) -> str:
    if minutos <= 5:
        return "🟢 0-5 min"
    if minutos <= 8:
        return "🟢 5-8 min"
    if minutos <= 12:
        return "🟡 8-12 min"
    if minutos <= 15:
        return "🟠 12-15 min"
    return "🔴 >15 min"


def mejor_acceso(accesos: list[AccesoTransporte]) -> AccesoTransporte | None:
    if not accesos:
        return None
    return min(accesos, key=lambda a: a.minutos_viaje_total)


def network_access_score(accesos: list[AccesoTransporte]) -> int:
    """Bonificación por multiacceso: más redes independientes = más resiliente."""
    redes_distintas = len({a.red for a in accesos})
    return BONUS_POR_CANTIDAD_LINEAS.get(redes_distintas, 15 if redes_distintas >= 4 else 0)


def transport_access_score(accesos: list[AccesoTransporte]) -> int:
    """0-100. Basado en el mejor acceso disponible + bonificación por redundancia."""
    if not accesos:
        return 30  # sin datos cargados: score conservador, no 0 (evita descartar por falta de carga)

    mejor = mejor_acceso(accesos)
    base = max(20, 100 - mejor.minutos_viaje_total * 1.2 - mejor.combinaciones * 8)
    bonus = network_access_score(accesos)
    return int(min(100, base + bonus))


def resumen_para_tabla(accesos: list[AccesoTransporte]) -> tuple[str, str]:
    """Devuelve (tiempo_texto, transporte_texto) para la columna Viaje/Transporte."""
    mejor = mejor_acceso(accesos)
    if mejor is None:
        return "N/D", "sin datos"
    icono = "🚆" if mejor.tipo == "tren" else "🚌"
    extra = f" + {mejor.combinaciones} comb." if mejor.combinaciones else ""
    return f"{mejor.minutos_viaje_total} min", f"{icono} {mejor.red}{extra}"


def detalle_accesos(accesos: list[AccesoTransporte]) -> str:
    if not accesos:
        return "Sin datos de transporte cargados."
    lineas = []
    for a in sorted(accesos, key=lambda x: x.minutos_viaje_total):
        icono = "🚆" if a.tipo == "tren" else "🚌"
        lineas.append(f"{icono} {a.red}: {a.minutos_viaje_total} min totales, {a.minutos_caminata} min de caminata, "
                       f"{a.combinaciones} combinaciones ({_tiempo_a_nivel(a.minutos_caminata)} caminando)")
    return "\n".join(lineas)
