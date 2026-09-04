"""Lista de cadenas grandes a excluir de los resultados (no son mercado oculto).
Editable sin tocar código: data/exclusiones.yaml, una línea por cadena.
"""
import re
from pathlib import Path

import yaml

EXCLUSIONES_PATH = Path(__file__).resolve().parent.parent / "data" / "exclusiones.yaml"


def _cargar_cadenas() -> list[str]:
    if not EXCLUSIONES_PATH.exists():
        return []
    data = yaml.safe_load(EXCLUSIONES_PATH.read_text(encoding="utf-8")) or {}
    return [c.strip() for c in data.get("cadenas_excluidas", []) if c.strip()]


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9áéíóúñ ]+", "", texto)
    return texto.strip()


def es_cadena_excluida(nombre_empresa: str) -> str | None:
    """Devuelve el nombre de la cadena que matcheó, o None si no está excluida."""
    nombre_norm = _normalizar(nombre_empresa)
    for cadena in _cargar_cadenas():
        cadena_norm = _normalizar(cadena)
        if cadena_norm and cadena_norm in nombre_norm:
            return cadena
    return None


# CABA está prohibida: Marco no puede viajar hasta ahí (regla dura, no de
# prioridad baja — se descarta automáticamente, no se muestra nunca). Se
# chequea contra la zona de búsqueda y contra la dirección resuelta por
# geocodificación (nunca contra el nombre de la empresa, para evitar falsos
# positivos con apellidos/marcas que coincidan con un barrio).
ZONAS_PROHIBIDAS = [
    "CABA", "Capital Federal", "Ciudad Autonoma de Buenos Aires",
    "Ciudad Autónoma de Buenos Aires", "Ciudad de Buenos Aires",
]


def es_zona_prohibida(zona_o_direccion: str) -> str | None:
    if not zona_o_direccion:
        return None
    texto_norm = _normalizar(zona_o_direccion)
    for prohibida in ZONAS_PROHIBIDAS:
        prohibida_norm = _normalizar(prohibida)
        if prohibida_norm and prohibida_norm in texto_norm:
            return prohibida
    return None
