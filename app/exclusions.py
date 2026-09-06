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
    """Devuelve el nombre de la cadena que matcheó, o None si no está excluida.

    Bug real encontrado: "Dia" (la cadena Día) matcheaba como substring
    contra "Diaz"/"Díaz" — CUALQUIER empresa con ese apellido (muy común en
    Argentina) se excluía por error, pensando que era el supermercado.
    Coincidencia por palabra completa, no substring suelto."""
    nombre_norm = _normalizar(nombre_empresa)
    palabras_nombre = set(nombre_norm.split())
    for cadena in _cargar_cadenas():
        cadena_norm = _normalizar(cadena)
        if not cadena_norm:
            continue
        palabras_cadena = cadena_norm.split()
        if len(palabras_cadena) == 1:
            # cadena de una sola palabra (ej. "Dia", "Coto"): debe coincidir
            # como palabra completa, no como substring de otra palabra
            if palabras_cadena[0] in palabras_nombre:
                return cadena
        elif cadena_norm in nombre_norm:
            # cadena de varias palabras (ej. "Mercado Libre", "La Anonima"):
            # substring de frase completa sigue siendo seguro
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


# Agencias de RRHH / staffing / búsqueda de personal: son intermediarias,
# no el empleador real. Detección por patrón (no por marca fija) para que
# agarre cualquiera — chica, mediana o grande —, no solo una lista cerrada
# de nombres. Las grandes genéricas (Randstad, Adecco, Manpower, Bayton,
# Gestión Compartida...) suelen caer solas por estos mismos patrones, así
# que no hace falta nombrarlas aparte.
PALABRAS_AGENCIA_RRHH = [
    "recursos humanos", "rrhh", "seleccion de personal", "selección de personal",
    "busqueda de personal", "búsqueda de personal", "busqueda y seleccion",
    "búsqueda y selección", "consultora de rrhh", "consultora de recursos humanos",
    "headhunter", "headhunting", "bolsa de empleo", "bolsa de trabajo",
    "outsourcing de personal", "provision de personal", "provisión de personal",
    "personal eventual", "personal temporario", "servicios eventuales",
    "empresa de servicios eventuales", "staffing", "reclutamiento y seleccion",
    "reclutamiento y selección",
    # bug real: "Servicios de Personal y Eventual" no matcheaba "personal
    # eventual" como frase fija (la "y" en el medio rompe el substring) —
    # frase más genérica que cubre esa variante y otras similares
    "servicios de personal", "provision de personal eventual",
]


def es_agencia_rrhh(nombre_o_descripcion: str) -> bool:
    """True si el texto (nombre o descripción de la empresa) parece una
    agencia de RRHH/staffing — se busca activamente para poder descartarla,
    no se asume que nunca va a aparecer."""
    texto_norm = _normalizar(nombre_o_descripcion or "")
    return any(_normalizar(p) in texto_norm for p in PALABRAS_AGENCIA_RRHH)


def es_zona_prohibida(zona_o_direccion: str) -> str | None:
    if not zona_o_direccion:
        return None
    texto_norm = _normalizar(zona_o_direccion)
    for prohibida in ZONAS_PROHIBIDAS:
        prohibida_norm = _normalizar(prohibida)
        if prohibida_norm and prohibida_norm in texto_norm:
            return prohibida
    return None
