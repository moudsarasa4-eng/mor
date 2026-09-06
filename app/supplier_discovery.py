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
    # supermercado alimentos bebidas
    "conservas de tomate", "conservas de vegetales", "aceites comestibles", "fideos secos",
    "harinas", "galletitas", "lácteos", "quesos", "embutidos", "productos de limpieza",
    "detergentes", "papel higiénico", "artículos de plástico para el hogar",
    "bebidas gaseosas", "aguas envasadas", "snacks", "golosinas",
    "productos de panificación congelados", "envases de vidrio", "envases plásticos",
    "productos textiles para el hogar", "yerba mate", "café", "té", "azúcar", "sal fina",
    "condimentos y especias", "salsas envasadas", "mermeladas", "miel",
    "cereales para desayuno", "alimentos congelados", "helados industriales", "vinos",
    "cervezas", "bebidas espirituosas", "jugos envasados", "aguas saborizadas",
    "productos de rotisería industrial", "panificados congelados",
    "productos de pastelería industrial", "chocolates industriales", "alimentos dietéticos",
    "alimentos para bebés", "conservas de pescado", "aceitunas envasadas", "encurtidos",
    "productos de granja", "huevos al por mayor",
    # construccion ferreteria
    "ladrillos", "cemento", "arena", "hierro para construcción", "maderas", "chapas", "caños",
    "cables", "pinturas", "cerámicos", "revestimientos", "aberturas", "herramientas",
    "tornillería", "sanitarios", "membranas", "áridos", "premoldeados", "andamios",
    "materiales eléctricos", "yeso", "cal", "hormigón elaborado", "bloques de hormigón",
    "perfiles de aluminio", "vidrios para construcción", "durlock", "aislantes térmicos",
    "aislantes acústicos", "impermeabilizantes", "selladores y adhesivos para construcción",
    "grifería", "artefactos de iluminación", "cajas eléctricas", "tableros eléctricos",
    "disyuntores y térmicas", "cerraduras", "herrajes para aberturas", "rejas y cercos",
    "portones", "techos de chapa", "tejas", "pisos flotantes", "porcelanato",
    "mármol y granito", "escaleras", "andamios tubulares", "encofrados", "maquinaria vial",
    "compresores de aire",
    # industria metalurgica autopartes
    "autopartes", "repuestos automotor", "neumáticos", "baterías", "lubricantes",
    "maquinaria industrial", "herramientas industriales", "insumos metalúrgicos",
    "chapa y pintura", "matricería", "fundición", "soldadura e insumos de soldadura",
    "aceros especiales", "aluminio industrial", "bulonería industrial", "rodamientos",
    "correas industriales", "válvulas industriales", "bombas industriales",
    "compresores industriales", "motores eléctricos industriales",
    "reductores y motorreductores", "sistemas hidráulicos", "sistemas neumáticos",
    "cintas transportadoras", "grúas y aparejos", "autoelevadores",
    "carretillas industriales", "estanterías metálicas industriales",
    "contenedores industriales", "repuestos de camiones", "repuestos de motos",
    "acoplados y remolques", "carrocerías", "insumos para talleres mecánicos",
    "filtros automotor", "amortiguadores", "frenos y embragues", "vidrios automotor",
    "gomería y vulcanización", "insumos náuticos", "repuestos náuticos",
    "insumos ferroviarios", "insumos para colectivos",
    # higiene indumentaria trabajo
    "insumos de limpieza industrial", "indumentaria de trabajo",
    "elementos de protección personal", "uniformes", "calzado de seguridad",
    "guantes industriales", "cascos de seguridad", "protección auditiva industrial",
    "ropa ignífuga", "productos de bioseguridad", "desinfectantes industriales",
    "insumos de seguridad e higiene laboral", "señalética de seguridad",
    "matafuegos y extintores", "botiquines industriales",
    # papel carton embalaje
    "envases y embalajes", "cartón corrugado", "papel para embalaje", "film stretch",
    "pallets", "cajas de cartón", "etiquetas", "packaging", "bolsas de papel",
    "bolsas plásticas industriales", "precintos y flejes", "cinta de embalar",
    "papel higiénico industrial", "papel tissue", "insumos gráficos", "tintas para impresión",
    "insumos para imprenta", "cartelería y señalética comercial",
    # plastico quimico
    "productos plásticos industriales", "químicos industriales", "agroquímicos",
    "pinturas industriales", "adhesivos industriales", "resinas plásticas",
    "solventes industriales", "productos de limpieza química",
    "envases plásticos industriales", "insumos para inyección plástica", "polímeros",
    "geotextiles", "membranas geotextiles",
    # muebles equipamiento
    "muebles de oficina", "mobiliario comercial", "estanterías industriales",
    "equipamiento para gastronomía", "refrigeración comercial", "cámaras frigoríficas",
    "góndolas y exhibidores", "colchones y sommiers", "mobiliario escolar",
    "mobiliario hospitalario", "sillas y sillones de oficina",
    "archivos y bibliotecas metálicas", "cortinas de enrollar", "toldos y coberturas",
    # agro
    "forrajes", "semillas", "insumos agropecuarios", "maquinaria agrícola", "fertilizantes",
    "semillas forestales", "insumos para vivero", "insumos para pileta", "sistemas de riego",
    "silos y almacenamiento de granos", "envases para agroquímicos", "insumos veterinarios",
    # service tecnico mantenimiento
    "service de aire acondicionado", "mantenimiento de ascensores", "matafuegos",
    "portones automáticos", "sistemas de seguridad CCTV", "plomería industrial",
    "electricidad industrial", "service de electrodomésticos", "service de informática",
    "mantenimiento de calderas", "service de bombas de agua", "mantenimiento de flotas",
    "service de grupos electrógenos", "instalación de gas", "mantenimiento edilicio",
    "limpieza de tanques de agua", "desinfección y control de plagas",
    "mantenimiento de jardines", "poda y espacios verdes", "service de computadoras",
    # textil indumentaria
    "telas", "indumentaria corporativa", "uniformes escolares", "textiles para el hogar",
    "hilados", "insumos textiles técnicos", "bordados y estampados textiles",
    "insumos de mercería", "calzado al por mayor", "marroquinería", "insumos para tapicería",
    # papeleria oficina informatica
    "artículos de librería", "insumos de oficina", "resmas de papel",
    "insumos de informática", "cartuchos y tóners", "computadoras al por mayor",
    "insumos de telefonía", "cableado estructurado", "insumos de electrónica",
    "baterías y pilas al por mayor",
    # farmacia salud estetica
    "insumos médicos", "insumos odontológicos", "productos de perfumería",
    "insumos para peluquería", "insumos de estética", "productos de cosmética al por mayor",
    "insumos hospitalarios", "equipamiento médico", "insumos para gimnasios",
    "suplementos deportivos",
    # energia climatizacion
    "energías renovables", "paneles solares", "climatización industrial",
    "insumos de gas envasado", "sistemas de calefacción", "grupos electrógenos",
    "insumos eléctricos de media tensión",
    # transporte logistica insumos
    "insumos para containers", "logística portuaria", "insumos para depósitos fiscales",
    "sistemas de trazabilidad logística", "insumos para transporte refrigerado",
    "equipamiento de carga y descarga", "insumos para bicicletas",
    "repuestos para bicicletas y motos eléctricas",
    # otros servicios b2b
    "insumos para lavaderos de autos", "insumos para lavanderías industriales",
    "insumos para tintorerías", "insumos para imprentas offset", "insumos para carpinterías",
    "insumos para vidrierías", "insumos para herrerías", "insumos para talleres de tapicería",
    "insumos para fábricas de muebles", "insumos para panaderías industriales",
    "insumos para heladerías artesanales", "insumos para rotiserías",
    "insumos para gastronomía", "insumos para catering", "insumos para eventos",
    "insumos para hotelería", "insumos para lavaderos industriales",
    "insumos para fábricas textiles", "insumos para call centers",
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
