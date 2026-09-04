"""Abstracción de proveedor de búsqueda — hoy solo hay Serper.dev conectado,
pero si algún día se agrega un segundo proveedor (por redundancia, o porque
Serper cambia su capa gratis), esto evita reescribir discovery.py/promote.py/
contact_finder.py: alcanza con implementar SearchProvider y registrarlo acá.

No activa nada por su cuenta — sin una segunda API key configurada, sigue
usando exclusivamente Serper, igual que antes.
"""
from abc import ABC, abstractmethod


class SearchProvider(ABC):
    nombre: str

    @abstractmethod
    def buscar(self, query: str, num: int = 20) -> dict:
        """Debe devolver un dict con la forma {"organic": [{"title", "link", "snippet"}, ...]}
        — el mismo formato que ya usa app.discovery.extraer_candidatas, para
        que cualquier proveedor nuevo sea un reemplazo directo sin tocar el
        resto del pipeline."""
        raise NotImplementedError


class SerperProvider(SearchProvider):
    nombre = "serper"

    def buscar(self, query: str, num: int = 20) -> dict:
        from app.search_client import buscar as _buscar_serper
        return _buscar_serper(query, num=num)


# Registro de proveedores disponibles. Agregar uno nuevo: implementar la clase
# arriba (ej. class BingProvider(SearchProvider): ...) y sumarlo acá con su
# nombre. app.search_client.buscar() sigue siendo el punto de entrada actual
# usado en todo el pipeline — este módulo queda listo para cuando haga falta
# un fallback real, sin forzar la migración hasta entonces.
PROVEEDORES: dict[str, SearchProvider] = {
    "serper": SerperProvider(),
}


def get_provider(nombre: str = "serper") -> SearchProvider:
    if nombre not in PROVEEDORES:
        raise ValueError(f"Proveedor de búsqueda desconocido: {nombre}. Disponibles: {list(PROVEEDORES)}")
    return PROVEEDORES[nombre]
