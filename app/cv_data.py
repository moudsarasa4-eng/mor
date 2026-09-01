"""Fuente única de verdad de los 4 CVs reales de Marco Ammazzalorso.
Extraído literal de los PDFs (cvs/*.txt). El generador de emails NUNCA debe usar
experiencia, certificaciones o habilidades que no estén acá.
"""

CANDIDATO = {
    "nombre": "Marco Ammazzalorso",
    "localidad": "Hurlingham, Buenos Aires",
    "email": "marcoamma04@gmail.com",
    "telefono": "+54 11 5513-5959",
    "disponibilidad": "Full time, turnos rotativos, fines de semana. Monotributista.",
}

CVS = {
    "administrativo": {
        "titulo": "Administrativo · Atención al Cliente · Manejo de Caja",
        "experiencia": [
            "atención personalizada al cliente en mostrador y caja (Arcos Dorados)",
            "manejo de caja registradora en horarios de alta demanda (Arcos Dorados)",
            "administración y carga de datos de clientes en sistema interno (comercio mayorista)",
            "control y seguimiento de stock: altas, bajas y movimientos de inventario (comercio mayorista)",
            "organización de documentación administrativa: remitos, facturas y órdenes de compra (comercio mayorista)",
        ],
        "certificaciones": [
            "Excel – De Básico a Intermedio (Santander Open Academy, 2026)",
            "Riesgo Biológico y Desinfección (Superintendencia de Riesgos del Trabajo, 2026)",
        ],
        "habilidades": ["atención al cliente", "manejo de caja", "administración", "carga de datos", "excel", "organización documental"],
        "necesidades_que_cubre": {"caja", "stock", "administracion", "atencion_publico", "excel", "documentacion"},
    },
    "atencion_cliente": {
        "titulo": "Atención al Cliente · Servicio de Caja",
        "experiencia": [
            "atención directa y personalizada al cliente en salón y caja (Arcos Dorados)",
            "toma de pedidos y servicio de caja en turnos de alta demanda (Arcos Dorados)",
            "recepción y atención personalizada a clientes, proveedores y visitas (comercio mayorista)",
            "manejo de caja y control de ingresos y egresos (comercio mayorista)",
        ],
        "certificaciones": [
            "Excel – De Básico a Intermedio (Santander Open Academy, 2026)",
            "Riesgo Biológico y Desinfección (Superintendencia de Riesgos del Trabajo, 2026)",
        ],
        "habilidades": ["atención al cliente", "servicio de caja", "comunicación", "resolución de consultas y reclamos"],
        "necesidades_que_cubre": {"caja", "atencion_publico", "trato_cliente", "mostrador"},
    },
    "limpieza": {
        "titulo": "Limpieza Profesional · Maestranza · Higiene y Seguridad",
        "experiencia": [
            "limpieza y cierre de locales al finalizar turno (Arcos Dorados)",
            "limpieza y desinfección de equipos de cocina (Arcos Dorados)",
            "limpieza de interiores y exteriores del restaurante (Arcos Dorados)",
            "limpieza y desinfección de áreas de depósito, sectores de trabajo y zonas comunes (comercio mayorista)",
            "manejo y uso adecuado de productos químicos de limpieza y desinfección (comercio mayorista)",
        ],
        "certificaciones": [
            "Limpieza y Desinfección Hospitalaria (Organización Panamericana de la Salud, OPS)",
            "Riesgo Biológico y Desinfección (Superintendencia de Riesgos del Trabajo, 2026)",
            "Excel – De Básico a Intermedio (Santander Open Academy, 2026)",
        ],
        "habilidades": ["limpieza y desinfección hospitalaria", "uso de EPP", "manejo de productos químicos", "control de residuos"],
        "necesidades_que_cubre": {"limpieza", "desinfeccion", "higiene", "riesgo_biologico", "hospitalaria", "epp"},
    },
    "logistica": {
        "titulo": "Logística · Depósito · Control de Stock · Mantenimiento",
        "experiencia": [
            "carga y descarga de mercadería e insumos (Arcos Dorados)",
            "mantenimiento general de instalaciones y equipos (Arcos Dorados)",
            "control de recepción de mercadería e insumos (Arcos Dorados)",
            "control y seguimiento de stock: altas, bajas y movimientos de inventario (comercio mayorista)",
            "recepción, clasificación y verificación de mercadería ingresante (comercio mayorista)",
            "preparación y despacho de pedidos según órdenes de compra (comercio mayorista)",
            "carga de remitos, facturas y documentación logística en sistema interno (comercio mayorista)",
        ],
        "certificaciones": [
            "Riesgo Biológico y Desinfección (Superintendencia de Riesgos del Trabajo, 2026)",
            "Excel – De Básico a Intermedio (Santander Open Academy, 2026)",
        ],
        "habilidades": ["carga y descarga", "control de stock e inventario", "mantenimiento general", "documentación logística", "EPP"],
        "necesidades_que_cubre": {"deposito", "expedicion", "recepcion", "stock", "carga_descarga", "mantenimiento", "documentacion_logistica"},
    },
}


def experiencia_relevante(cv: str, necesidades: set[str], max_items: int = 2) -> list[str]:
    """Devuelve hasta max_items frases de experiencia REAL, priorizando las que
    mejor cubren las necesidades inferidas de la empresa. Nunca inventa nada:
    solo selecciona entre lo que ya existe en CVS[cv]['experiencia']."""
    items = CVS[cv]["experiencia"]
    if not necesidades:
        return items[:max_items]

    def score(frase: str) -> int:
        frase_l = frase.lower()
        return sum(1 for n in necesidades if n.replace("_", " ") in frase_l)

    ordenadas = sorted(items, key=score, reverse=True)
    return ordenadas[:max_items]


def certificacion_relevante(cv: str, necesidades: set[str]) -> str | None:
    cubiertas = CVS[cv]["necesidades_que_cubre"] & necesidades
    if not cubiertas:
        return None
    certs = CVS[cv]["certificaciones"]
    return certs[0] if certs else None
