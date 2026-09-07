"""Diccionario semilla de keywords + plantillas de query por intención (Types A-G).
El motor puede ampliar este diccionario con app.discovery.registrar_keyword_descubierta().
"""

KEYWORDS_SEED = {
    "logistica": [
        "logística", "depósito", "distribución", "distribuidora", "centro de distribución",
        "centro logístico", "expedición", "despacho", "almacén", "operador logístico",
        "mayorista", "última milla", "flota de camiones", "transporte de cargas",
        "depósito fiscal", "cross docking", "operador logístico tercerizado",
    ],
    "administrativo": [
        "administración", "administrativo", "oficina", "gestión", "back office",
        "facturación", "estudio contable", "estudio jurídico", "inmobiliaria",
        "tercerización administrativa", "outsourcing administrativo", "consultora",
    ],
    "atencion_cliente": [
        "atención al cliente", "recepción", "mostrador", "ventas", "concesionaria",
        "supermercado", "retail", "call center", "telemarketing", "servicio postventa",
    ],
    "limpieza": [
        "limpieza", "higiene", "desinfección", "servicios generales", "facility",
        "mantenimiento", "limpieza industrial", "sanatorio", "clínica",
        # ejemplo de "entramado": una empresa de limpieza de trenes no aparece
        # buscando "limpieza" a secas, pero investigarla puede llevar a otras
        # tercerizadas (flota, colectivos, obra) con más rubros dentro
        "limpieza de trenes", "limpieza de flota", "limpieza de colectivos",
        "limpieza de vehículos", "limpieza post obra", "limpieza de oficinas",
        "empresa de limpieza tercerizada",
    ],
    "general": [
        "fábrica", "industria", "planta", "empresa", "comercio", "constructora",
        "hotel", "colegio privado", "centro médico",
        # se buscan activamente para poder descartarlas (no son el empleador
        # real) — no una lista fija de marcas, un patrón genérico de rubro
        "agencia de recursos humanos", "empresa de personal eventual", "staffing",
    ],
}

NOISE_TERMS_INICIALES = [
    "bumeran", "computrabajo", "indeed", "zonajobs", "linkedin jobs", "jooble",
    "simplyhired", "empleos.clarin",
]

DOMINIOS_EXCLUIR = [
    "bumeran.com", "computrabajo.com", "indeed.com", "zonajobs.com",
    "linkedin.com", "jooble.org", "simplyhired.com", "empleos.clarin.com",
    # detectado en corrida real: portal de avisos de empleo, mismo motivo que los de arriba
    "opcionempleo.com.ar",
]

DOMINIOS_RUIDO_NO_EMPRESA = [
    "wikipedia.org", "facebook.com/photo", "instagram.com/p/", "youtube.com",
    "mercadolibre.com", "twitter.com", "x.com",
    # inmobiliarias (avisos de depósito/galpón en alquiler/venta, no son la empresa)
    "zonaprop.com.ar", "argenprop.com", "properati.com.ar", "mercadolibre.com.ar/inmuebles",
    "openhousebsas.org", "buscainmueble.com", "enalquiler.com",
    # pasajes / transporte de pasajeros, no logística de carga
    "plataforma10.com", "omnilineas.com", "central-de-pasajes.com.ar", "moovitapp.com",
    # rankings / prensa genérica, no la empresa en sí
    "rankia.com", "merco.info", "elmundo.es", "eleconomista.com.mx", "cronista.com",
    "clarin.com", "ambito.com", "uada.org.ar", "cafydma.org", "primerplanoonline.com.ar",
    "agrofy.com.ar",
    # diccionarios / definiciones (el nombre de una zona puede coincidir con
    # una palabra común del español, ej. "Caseros" = "casero" = "de la casa")
    "wordreference.com", "wiktionary.org", "merriam-webster.com", "dle.rae.es",
    "significados.com", "definicion.de", "collinsdictionary.com", "thefreedictionary.com",
    "economipedia.com",
    # blogs de SaaS / marketing genéricos, no son un empleador real
    "zendesk.com", "wix.com", "hubspot.com", "shopify.com", "oracle.com",
    "gestionbackoffice.com", "drvsistemas.com", "themanifest.com", "exact.com.pe",
    "prosource.com.co", "hyland.com", "emergenresearch.com", "thecfoclub.com",
    # software de facturación (SaaS, no son un empleador real)
    "facturasimple.com", "facturify.com", "facturalia.info", "csfacturacion.com",
    "pimedigital.com", "sendfactura.com",
    # contenido educativo de EEUU sin relación (se cuela con keywords de salud)
    "bestcolleges.com", "nursingprocess.org", "nursingschoolhub.com",
    "randstad.com.au", "research.com", "registerednursing.org",
    # medios/radio genéricos, no una empresa
    "los40.com", "enter.co",
    # instagram: perfiles y posts (antes solo se excluía /p/, no el perfil general)
    "instagram.com",
    # directorios/registros de empresas — confirman que existen, pero la
    # página en sí no es la empresa (ya se cubre lo mismo con
    # site:cuitonline.com como fuente de búsqueda dirigida)
    "emis.com", "dateas.com", "datok.com.ar", "dunsguide.com", "arempresas.com",
    "buscargentina.net", "starofservice.com.ar", "cybo.com", "es.cybo.com",
    "licuo.com.ar", "argentino.com.ar", "redargentina.com.ar", "infoisinfo-ar.com",
    "guiaurbana.com.ar", "manufactura-latam.com", "all.biz", "empresia.es",
    "granguiaargentina.com.ar", "negozona.com",
    # registros de empresas extranjeros (Perú, Colombia, Brasil, España) —
    # se cuelan con búsquedas genéricas de rubro sin filtro geográfico real
    "cnpj.biz", "rues.org.co", "universidadperu.com", "contadormype.pe", "bosperu.com",
    "datosperu.org",
    # educativo/gobierno genérico sin relación, mapas de POIs (no son la empresa)
    "oerproject.com", "archive.epa.gov", "mapcarta.com",
    # blogs / artículos genéricos, no una empresa
    "substack.com", "opcionempleo.com",
    # agregadores de turismo/reseñas/empleo que se colaron en el análisis de
    # un archivo real de 1787 candidatas (zona Martín Coronado/Morón/Ramos
    # Mejía): hoteles, alquileres temporarios, rankings de "mejores empresas"
    "trip.com", "glassdoor.com", "glassdoor.com.ar", "airbnb.com", "habitissimo.com.ar",
]


# exclusiones aplicadas a TODAS las queries: países homónimos que generan falsos
# positivos (Trujillo/Lima en Perú, etc.) y avisos inmobiliarios/pasajes que no
# son la empresa buscada — más barato filtrar en la query que gastar presupuesto
# trayendo el resultado para descartarlo después.
# "Bella Vista" (zona configurada) es homónimo de ciudades en EEUU
# (Arkansas/Missouri), México (Chiapas), Chile, Guatemala — muchos de esos
# negocios no mencionan el país en el texto, así que filtrarlos después por
# patrón no alcanza. Es mucho más barato excluirlos en la query misma.
EXCLUSIONES_QUERY = (
    "-Peru -Trujillo -Lima -México -Chile -Colombia -España -Zonaprop -Argenprop -pasajes "
    "-Arkansas -Missouri -Guatemala -Chiapas -\"Estados Unidos\""
)


def plantillas_query(zona: str, keyword: str = "") -> list[dict]:
    """Devuelve queries tipadas (Type A-G) para una zona, opcionalmente centradas
    en una keyword específica."""
    q = []
    kw = keyword or ""
    sufijo = f" {EXCLUSIONES_QUERY}"
    if kw:
        q.append({"query": f"empresas {kw} {zona}{sufijo}", "tipo": "TYPE_A", "keyword": kw})
        q.append({"query": f"\"{kw}\" {zona} -{' -'.join(NOISE_TERMS_INICIALES[:4])}{sufijo}", "tipo": "TYPE_A", "keyword": kw})
        # directorios de empresas argentinos (Páginas Amarillas, CUIT Online no
        # tienen API gratuita masiva para descubrir por rubro, pero sus páginas
        # SÍ están indexadas — sin este site: el buscador de texto normal casi
        # nunca las trae arriba de los resultados).
        q.append({"query": f"site:paginasamarillas.com.ar {kw} {zona}{sufijo}", "tipo": "TYPE_H", "keyword": kw})
        q.append({"query": f"site:cuitonline.com {kw} {zona}{sufijo}", "tipo": "TYPE_H", "keyword": kw})
        # la red dir.ar (logística, limpieza, administración de consorcios,
        # catering, gimnasios, tiendas de ropa, salud y belleza, seguridad
        # del hogar, talleres mecánicos, gráficas e imprentas, abogados,
        # transporte) YA NO se busca acá vía site: (eso gasta presupuesto de
        # Serper) — se lee directo y gratis en app/directorio_dir_ar.py,
        # enganchado al ciclo automático en runner.py como fuente aparte.
    else:
        # estas NO dependen de la keyword (el texto de la query es siempre el
        # mismo) — antes se generaban igual dentro del bloque de arriba, así
        # que se armaban una vez POR CADA keyword (70+ veces, todas con el
        # mismo texto): un desperdicio real de presupuesto, ya que la llamada
        # sin keyword (una sola vez por zona, en runner._generar_lote_queries)
        # alcanza para cubrirlas.
        q.append({"query": f"principales empresas {zona}{sufijo}", "tipo": "TYPE_B", "keyword": kw})
        q.append({"query": f"fábricas industrias {zona}{sufijo}", "tipo": "TYPE_C", "keyword": kw})
        q.append({"query": f"empresa {zona} expansión OR inversión OR \"nueva planta\" OR ampliación{sufijo}", "tipo": "TYPE_E", "keyword": kw})
        q.append({"query": f"empresa {zona} depósito OR planta OR sucursal OR \"centro logístico\"{sufijo}", "tipo": "TYPE_F", "keyword": kw})
        q.append({"query": f"\"parque industrial\" {zona} empresas instaladas{sufijo}", "tipo": "TYPE_F", "keyword": kw})
    return q
