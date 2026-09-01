"""Diccionario semilla de keywords + plantillas de query por intención (Types A-G).
El motor puede ampliar este diccionario con app.discovery.registrar_keyword_descubierta().
"""

KEYWORDS_SEED = {
    "logistica": [
        "logística", "depósito", "distribución", "distribuidora", "centro de distribución",
        "centro logístico", "expedición", "despacho", "almacén", "operador logístico",
        "mayorista",
    ],
    "administrativo": [
        "administración", "administrativo", "oficina", "gestión", "back office",
        "facturación", "estudio contable", "estudio jurídico", "inmobiliaria",
    ],
    "atencion_cliente": [
        "atención al cliente", "recepción", "mostrador", "ventas", "concesionaria",
        "supermercado", "retail",
    ],
    "limpieza": [
        "limpieza", "higiene", "desinfección", "servicios generales", "facility",
        "mantenimiento", "limpieza industrial", "sanatorio", "clínica",
    ],
    "general": [
        "fábrica", "industria", "planta", "empresa", "comercio", "constructora",
        "hotel", "colegio privado", "centro médico",
    ],
}

NOISE_TERMS_INICIALES = [
    "bumeran", "computrabajo", "indeed", "zonajobs", "linkedin jobs", "jooble",
    "simplyhired", "empleos.clarin",
]

DOMINIOS_EXCLUIR = [
    "bumeran.com", "computrabajo.com", "indeed.com", "zonajobs.com",
    "linkedin.com", "jooble.org", "simplyhired.com", "empleos.clarin.com",
]

DOMINIOS_RUIDO_NO_EMPRESA = [
    "wikipedia.org", "facebook.com/photo", "instagram.com/p/", "youtube.com",
    "mercadolibre.com", "twitter.com", "x.com",
]


def plantillas_query(zona: str, keyword: str = "") -> list[dict]:
    """Devuelve queries tipadas (Type A-G) para una zona, opcionalmente centradas
    en una keyword específica."""
    q = []
    kw = keyword or ""
    if kw:
        q.append({"query": f"empresas {kw} {zona}", "tipo": "TYPE_A", "keyword": kw})
        q.append({"query": f"\"{kw}\" {zona} -{' -'.join(NOISE_TERMS_INICIALES[:4])}", "tipo": "TYPE_A", "keyword": kw})
    q.append({"query": f"principales empresas {zona}", "tipo": "TYPE_B", "keyword": kw})
    q.append({"query": f"fábricas industrias {zona}", "tipo": "TYPE_C", "keyword": kw})
    q.append({"query": f"empresa {zona} expansión OR inversión OR \"nueva planta\" OR ampliación", "tipo": "TYPE_E", "keyword": kw})
    q.append({"query": f"empresa {zona} depósito OR planta OR sucursal OR \"centro logístico\"", "tipo": "TYPE_F", "keyword": kw})
    q.append({"query": f"\"parque industrial\" {zona} empresas instaladas", "tipo": "TYPE_F", "keyword": kw})
    return q
