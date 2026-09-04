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


VELOCIDAD_CAMINATA_KMH = 5.0  # promedio adulto, para estimar minutos desde metros


def _coords_estacion(nombre_estacion: str):
    """Geocodifica una estación (vía OSM Nominatim, cacheado en estaciones_cache
    para no re-pedirla cada vez — respeta el límite de 1 req/seg de Nominatim)."""
    from app.db import get_conn, now
    from app.geocoding import geocodificar

    conn = get_conn()
    row = conn.execute("SELECT lat, lon FROM estaciones_cache WHERE nombre=?", (nombre_estacion,)).fetchone()
    if row:
        conn.close()
        return row["lat"], row["lon"]

    coords = geocodificar(f"Estación {nombre_estacion}, Línea San Martín, Buenos Aires, Argentina")
    conn.close()
    if coords is None:
        return None
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO estaciones_cache (nombre, lat, lon, creado_en) VALUES (?, ?, ?, ?)",
                 (nombre_estacion, coords.lat, coords.lon, now()))
    conn.commit()
    conn.close()
    return coords.lat, coords.lon


def estacion_mas_cercana(lat: float, lon: float) -> dict | None:
    """Compara la posición dada contra las estaciones de la Línea San Martín
    (por coordenadas reales, geocodificadas y cacheadas) y devuelve la más
    cercana con distancia y minutos de caminata ESTIMADOS (velocidad promedio,
    no tiene en cuenta veredas/cruces reales). NO calcula el viaje en tren en
    sí ni combinaciones con colectivo — para eso sigue haciendo falta cargar
    el dato real a mano con app.transport."""
    from app.geocoding import distancia_haversine_metros

    mejor = None
    for estacion in LINEA_SAN_MARTIN:
        coords = _coords_estacion(estacion)
        if coords is None:
            continue
        e_lat, e_lon = coords
        metros = distancia_haversine_metros(lat, lon, e_lat, e_lon)
        if mejor is None or metros < mejor["distancia_metros"]:
            mejor = {
                "estacion": estacion,
                "distancia_metros": round(metros),
                "minutos_caminata_estimados": round(metros / 1000 / VELOCIDAD_CAMINATA_KMH * 60),
            }
    return mejor
