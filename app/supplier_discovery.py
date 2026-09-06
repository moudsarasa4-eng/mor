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
from app.keywords import EXCLUSIONES_QUERY

# Categorías de producto/material/servicio — "método envolvente": no se
# busca el puesto, se busca quién provee/fabrica/distribuye/da service de
# algo concreto en la zona. Esa empresa casi nunca publica una vacante, pero
# tiene depósito, administración, compras y atención a clientes igual — los
# 4 rubros del CV, sin competir con nadie que busque por portal de empleo.
# Ver docs/PALABRAS_ENVOLVENTES.md para la investigación completa por
# categoría y por qué cada una genera pistas de estos 4 rubros.
CATEGORIAS_PRODUCTO = [
    # supermercado / alimentos y bebidas (logística de reparto)
    "conservas de tomate", "conservas de vegetales", "aceites comestibles",
    "fideos secos", "harinas", "galletitas", "lácteos", "quesos",
    "embutidos", "productos de limpieza", "detergentes", "papel higiénico",
    "artículos de plástico para el hogar", "bebidas gaseosas", "aguas envasadas",
    "snacks", "golosinas", "productos de panificación congelados",
    "envases de vidrio", "envases plásticos", "productos textiles para el hogar",
    # construcción / ferretería (mucho depósito y logística)
    "ladrillos", "cemento", "arena", "hierro para construcción", "maderas",
    "chapas", "caños", "cables", "pinturas", "cerámicos", "revestimientos",
    "aberturas", "herramientas", "tornillería", "sanitarios", "membranas",
    "áridos", "premoldeados", "andamios", "materiales eléctricos",
    # industria / metalúrgica / autopartes
    "autopartes", "repuestos automotor", "neumáticos", "baterías",
    "lubricantes", "maquinaria industrial", "herramientas industriales",
    "insumos metalúrgicos", "chapa y pintura", "matricería", "fundición",
    # higiene / indumentaria de trabajo (rubro directo de limpieza)
    "insumos de limpieza industrial", "indumentaria de trabajo",
    "elementos de protección personal", "uniformes",
    # papel, cartón, embalaje (logística intensiva)
    "envases y embalajes", "cartón corrugado", "papel para embalaje",
    "film stretch", "pallets", "cajas de cartón", "etiquetas", "packaging",
    # plástico / químico
    "productos plásticos industriales", "químicos industriales",
    "agroquímicos", "pinturas industriales", "adhesivos industriales",
    # muebles / equipamiento de oficina y comercio
    "muebles de oficina", "mobiliario comercial", "estanterías industriales",
    "equipamiento para gastronomía", "refrigeración comercial",
    "cámaras frigoríficas", "góndolas y exhibidores",
    # agro (zona oeste GBA tiene actividad rural residual)
    "forrajes", "semillas", "insumos agropecuarios", "maquinaria agrícola",
    "fertilizantes",
    # service técnico / mantenimiento (talleres con necesidad de todo)
    "service de aire acondicionado", "mantenimiento de ascensores",
    "matafuegos", "portones automáticos", "sistemas de seguridad CCTV",
    "plomería industrial", "electricidad industrial",
    "service de electrodomésticos", "service de informática",
]


def _queries_por_categoria(categoria: str, zona: str) -> list[dict]:
    s = f" {EXCLUSIONES_QUERY}"
    return [
        {"query": f'"quién fabrica" {categoria} Argentina{s}', "tipo": "TYPE_SUPPLIER", "keyword": categoria},
        {"query": f'"proveedor de" {categoria} {zona} OR "Buenos Aires"{s}', "tipo": "TYPE_SUPPLIER", "keyword": categoria},
        {"query": f'fabricante {categoria} "zona oeste" Buenos Aires{s}', "tipo": "TYPE_SUPPLIER", "keyword": categoria},
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
        # pendientes(zona) ya excluye lo recién procesado (queries_log se
        # actualiza en cada llamada) — restar len(resultados) de nuevo
        # duplicaba el descuento y subestimaba lo que falta.
        "pendientes_restantes": len(pendientes(zona)),
        "empresas_nuevas_totales": sum(r["empresas_nuevas"] for r in resultados),
        "detalle": resultados,
    }
