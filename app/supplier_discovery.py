"""Caza de proveedores por ingeniería inversa de góndola: las cadenas grandes
(Carrefour, Día, Coto...) no son destino de outreach, pero sus categorías de
producto sí sirven como pista para encontrar al fabricante/proveedor real
detrás de cada línea — que suele ser una empresa mediana, con estructura,
y mucho más receptiva a una postulación espontánea que la cadena misma.

Reusa el mismo pipeline de búsqueda/dedupe/promoción que el resto del motor.
"""
from app.db import get_conn, now
from app.discovery import ejecutar_query
from app.promote import promover_candidatas

# Categorías de producto típicas de supermercado, mapeadas a por qué generan
# pistas de fabricantes con necesidad de depósito/logística/administración.
CATEGORIAS_PRODUCTO = [
    "conservas de tomate", "conservas de vegetales", "aceites comestibles",
    "fideos secos", "harinas", "galletitas", "lácteos", "quesos",
    "embutidos", "productos de limpieza", "detergentes", "papel higiénico",
    "artículos de plástico para el hogar", "bebidas gaseosas", "aguas envasadas",
    "snacks", "golosinas", "productos de panificación congelados",
    "envases de vidrio", "envases plásticos", "productos textiles para el hogar",
]


def _queries_por_categoria(categoria: str, zona: str) -> list[dict]:
    return [
        {"query": f'"quién fabrica" {categoria} Argentina', "tipo": "TYPE_SUPPLIER", "keyword": categoria},
        {"query": f'"proveedor de" {categoria} {zona} OR "Buenos Aires"', "tipo": "TYPE_SUPPLIER", "keyword": categoria},
        {"query": f'fabricante {categoria} "zona oeste" Buenos Aires', "tipo": "TYPE_SUPPLIER", "keyword": categoria},
    ]


def pendientes(zona: str) -> list[str]:
    conn = get_conn()
    procesadas = {
        r["keyword"] for r in conn.execute(
            "SELECT DISTINCT keyword FROM queries_log WHERE zona=? AND tipo='TYPE_SUPPLIER'", (zona,)
        )
    }
    conn.close()
    return [c for c in CATEGORIAS_PRODUCTO if c not in procesadas]


def procesar_categoria(categoria: str, zona: str) -> dict:
    queries = _queries_por_categoria(categoria, zona)
    nuevas = 0
    for q in queries:
        r = ejecutar_query(q["query"], zona, q["tipo"], q["keyword"])
        nuevas += r.get("empresas_nuevas", 0)
    promover_candidatas(zona=zona)
    return {"categoria": categoria, "zona": zona, "empresas_nuevas": nuevas}


def correr_lote(zona: str, max_categorias: int = 5) -> dict:
    tareas = pendientes(zona)[:max_categorias]
    resultados = [procesar_categoria(c, zona) for c in tareas]
    return {
        "procesadas": len(resultados),
        "pendientes_restantes": len(pendientes(zona)) - len(resultados),
        "empresas_nuevas_totales": sum(r["empresas_nuevas"] for r in resultados),
        "detalle": resultados,
    }
