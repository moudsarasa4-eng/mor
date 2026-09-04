"""Referencia salarial por rubro — datos reales citados, con fecha, no
inventados. Se usa como estimación de partida para TODAS las candidatas
(no solo las que yo puntúo a mano), mostrada en el output de cada tanda.

Fuente y fecha de cada rango quedan explícitas porque los sueldos en
Argentina se desactualizan rápido (paritarias trimestrales). Revisar y
actualizar este archivo cada tanto — no asumir que sigue vigente para
siempre.
"""

SALARIOS_REFERENCIA = {
    "logistica": {
        "min": 900_000,
        "max": 1_400_000,
        "fuente": "Convenio Carga y Descarga (básico mensual ~$1.896.375 categoría 1, jun-2026) "
                   "y mediana de mercado Computrabajo (~$733.052, 2026) — rango entry-level estimado entre ambos",
        "fecha_referencia": "2026-06",
        "confianza": "media",
    },
    "administrativo": {
        "min": 850_000,
        "max": 1_300_000,
        "fuente": "Piso SMVM (~$367.800, jun-2026) + banda análoga a categorías administrativas de "
                   "Convenio Comercio CCT 130/75 — datos de portales de sueldos (Glassdoor) descartados "
                   "por inconsistencia en la muestra",
        "fecha_referencia": "2026-06",
        "confianza": "baja",
    },
    "atencion_cliente": {
        "min": 1_171_000,
        "max": 1_283_000,
        "fuente": "Básico Cajero A-C, Convenio Comercio CCT 130/75 (dic-2025 a ago-2026, La Gaceta/Infobae/FortunaWeb)",
        "fecha_referencia": "2026-08",
        "confianza": "alta",
    },
    "limpieza": {
        "min": 502_670,
        "max": 990_934,
        "fuente": "Operario de limpieza categoría inicial, jornada reducida a completa, Convenio Maestranza (Los Andes, may-2026)",
        "fecha_referencia": "2026-05",
        "confianza": "alta",
    },
}


def estimar_sueldo(rubro: str) -> dict | None:
    return SALARIOS_REFERENCIA.get(rubro)
