"""Geographic Intelligence — usa la Línea San Martín como columna vertebral,
expandiendo desde Hurlingham hacia ambos lados, sin forzar orden estricto:
un jackpot excepcional lejos puede investigarse antes que una estación cercana sin nada.
"""

LINEA_SAN_MARTIN = [
    "Retiro", "Palermo", "Villa Crespo", "La Paternal", "Villa del Parque",
    "Devoto", "Saenz Peña", "Santos Lugares", "Caseros", "El Palomar",
    "Hurlingham", "William Morris", "Bella Vista", "Muñiz", "San Miguel",
    "Jose C Paz", "Sol y Verde", "Derqui", "Villa Astolfi", "Pilar",
    "Manzanares", "Dr Cabred",
]

HURLINGHAM_IDX = LINEA_SAN_MARTIN.index("Hurlingham")


def distancia_estaciones(zona: str) -> int | None:
    if zona not in LINEA_SAN_MARTIN:
        return None
    return abs(LINEA_SAN_MARTIN.index(zona) - HURLINGHAM_IDX)


def accessibility_score(zona: str, tiene_otro_transporte: bool = False) -> int:
    """0-100. Más cerca de la línea San Martín / Hurlingham = mejor accesibilidad."""
    dist = distancia_estaciones(zona)
    if dist is None:
        # zona fuera de la línea: depende de si hay otro transporte directo
        return 55 if tiene_otro_transporte else 30
    if dist == 0:
        return 100
    # decae con la distancia en estaciones, piso en 40 si sigue sobre la línea
    return max(40, 100 - dist * 6)


def zonas_expandidas_ambos_lados(radio_estaciones: int = 6) -> list[str]:
    ini = max(0, HURLINGHAM_IDX - radio_estaciones)
    fin = min(len(LINEA_SAN_MARTIN), HURLINGHAM_IDX + radio_estaciones + 1)
    return LINEA_SAN_MARTIN[ini:fin]
