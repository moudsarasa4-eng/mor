"""Search Intelligence Engine — genera queries, busca, extrae candidatas,
deduplica, y aprende qué keywords/queries rinden mejor.

Heurística de extracción (limitación conocida, ver README): sin un LLM conectado,
la extracción de "nombre de empresa" desde título/snippet es basada en reglas, no
en comprensión real. Puede generar falsos positivos que se filtran después en la
etapa de verificación humana/asistida.
"""
import re
import time
from datetime import date

from app.db import get_conn, now
import app.search_client as search_client
from app.search_client import SearchClientError
from app.keywords import KEYWORDS_SEED, DOMINIOS_EXCLUIR, DOMINIOS_RUIDO_NO_EMPRESA, plantillas_query

SUFIJOS_A_LIMPIAR = [
    r"\s*[-|–]\s*LinkedIn.*$", r"\s*[-|–]\s*Facebook.*$", r"\s*\|\s*Facebook.*$",
    r"\s*[-|–]\s*Instagram.*$", r"\s*[-|–]\s*P[aá]ginas Amarillas.*$",
    r"\s*[-|–]\s*Argentina$", r"\s*\(\d{4}\)$", r"\s*[-|–]\s*Cylex.*$",
    r"\s*[-|–]\s*Wikipedia.*$", r"\s*[-|–]\s*Trabajo.*$", r"\s*[-|–]\s*Empleo.*$",
    r"\s*[-|–]\s*Cuit ?Online.*$", r"\s*[-|–]\s*Guiaurbana.*$", r"\s*[-|–]\s*P[aá]ginas Blancas.*$",
]

PALABRAS_EMPRESA_INDICADORAS = [
    "s.a.", "s.r.l.", "srl", "sa ", "distribuidora", "fábrica", "fabrica",
    "industria", "metalúrgica", "metalurgica", "empresa", "compañía", "grupo",
]

# Patrones que NO son una empresa aunque pasen el filtro de dominio: avisos
# inmobiliarios, pasajes/ómnibus, rankings/notas de prensa, resultados de
# otros países, y páginas puramente institucionales/genéricas.
PATRONES_NO_EMPRESA = [
    r"\ben (alquiler|venta)\b", r"\bm2\b", r"metros de\b", r"\bgalp[oó]n(es)?\b.*\b(venta|alquiler)\b",
    r"^\d+\s+dep[oó]sitos?\s+en\b",  # "30 Depósitos en Caseros"
    r"^pasajes?\s+de\b", r"\ba mar del\b", r"\bmnibus\b|\bmicro\b.*\bpasaje",
    r"^ranking\b", r"merco\s*empresas", r"^gracias por\b",
    r"^quienes somos\b", r"^qui[eé]nes somos\b", r"^inicio\s*[-|–]",
    r"\btrabajo de en\b",  # snippet roto típico de portal de empleo que se coló
    r"\ben (trujillo|lima|per[uú]|m[eé]xico|chile|colombia|espa[ñn]a)\b",  # país equivocado
    # país equivocado como palabra suelta (sin "en" adelante) — encontrado en
    # producción: "Bos Perú", "Contador Mype" (contadormype.pe), títulos que
    # mencionan el país sin la preposición "en"
    r"\b(per[uú]|peruano|peruana|mexicano|mexicana|colombiano|colombiana|brasil|brasile[ñn]o)\b",
    r"\b(salta|jujuy|misiones|neuqu[eé]n|chubut|chaco|resistencia)\b",  # otra provincia (ej. "Hotel Caseros Salta" — Caseros es homónimo de una calle en Salta)
    r"\bruc\s*:?\s*\d",  # RUC es el identificador tributario de Perú/otros países — Argentina usa CUIT
    # organismos estatales / licitaciones públicas: no son empleadores privados
    # accionables por postulación espontánea, el ingreso funciona distinto
    r"\b(anses|afip|licitaci[oó]n p[uú]blica|poder judicial|ministerio de)\b",
    # "Bella Vista" es homónimo de ciudades en EEUU (Arkansas/Missouri), Chile,
    # Guatemala — el bloqueo por ccTLD (.cl, .gt) no alcanza cuando el sitio usa
    # .com genérico (fedex.com, att.com, uber.com)
    r"\b(misuri|missouri|arkansas|guatemala|catarina)\b",
    # artículos tipo listicle / guía / definición — nunca son una empresa
    r"\b\d+\s+(mejores\s+)?(consejos|maneras|tipos|ideas|cosas|pasos|trucos)\b",
    r"^(c[oó]mo|qu[eé] es)\b.*\b(crear|hacer|abordar|mejorar|abrir)\b",
    # títulos de aviso de empleo que se colaron fuera de un portal excluido
    r"^(vendedor|cajero|operario|empleado|auxiliar|administrativo)\b.*\bzona\b",
    r"\bgu[ií]a para\b", r"\bgu[ií]a de\b",
    r"^definici[oó]n\b", r"^significado\b", r"\bdiccionario de la lengua\b",
    r"\bdefinition\s*&?\s*meaning\b", r"free dictionary\b", r"spanish to english\b",
    r"\b(best|most affordable|top)\b.*\b(programs?|degree|colleges?|schools?)\b",  # spam educativo en inglés
    r"instagram photos and videos\b",
    r"\b(cylex|guiaurbana|cercanooeste)\b",  # nombres de directorio, distintivos, no aparecen en nombres reales de empresa
]

# títulos que son solo una palabra genérica suelta — no aportan nada como nombre
PALABRAS_GENERICAS_SOLAS = {
    "empresas", "sucursales", "contacto", "inicio", "nosotros", "servicios",
    "productos", "novedades", "noticias", "contacto para empresas",
}
_PATRONES_NO_EMPRESA_COMPILADOS = [re.compile(p, re.IGNORECASE) for p in PATRONES_NO_EMPRESA]


# Detección de negocio unipersonal/muy chico: el motor filtraba "¿es real?
# ¿zona correcta? ¿no es cadena/agencia?" pero nunca "¿tiene tamaño para
# necesitar sumar personal?" — dejaba pasar mezclado un estudio de un solo
# abogado o un mecánico solo junto con empresas medianas reales. No se
# descarta (podría igual interesarle a Marco un puesto chico), pero se marca
# aparte para no confundirlo con una candidata seria.
PALABRAS_PROFESION_SOLO = [
    "abogado", "contador", "escribano", "kinesiologo", "kinesiólogo", "psicologo",
    "psicólogo", "profesor particular", "personal trainer", "coach ", "traductor",
    "medico a domicilio", "médico a domicilio", "asesor de imagen",
]
PALABRAS_INDICIO_ESTRUCTURA = [
    # "estudio" a secas es ambiguo (puede ser "atiendo en mi estudio" de un
    # solo profesional) — solo cuenta como indicio de estructura combinado
    # con socios/plural
    "asociados", "estudio jurídico", "estudio contable", "sucursales", "empleados",
    "equipo de", "planta", "depósito", "deposito", "flota", "sa ", "srl", "s.a",
    "s.r.l", "& ", " y asociados",
]


def _parece_negocio_unipersonal(nombre: str, descripcion: str = "") -> bool:
    palabras_nombre = nombre.strip().split()
    es_nombre_persona = len(palabras_nombre) == 2 and all(p[:1].isupper() for p in palabras_nombre)
    texto = (descripcion or "").lower()
    nombre_l = nombre.lower()
    tiene_marca_profesion_solo = any(p in texto for p in PALABRAS_PROFESION_SOLO)
    tiene_indicio_estructura = (
        any(ind in texto for ind in PALABRAS_INDICIO_ESTRUCTURA)
        or any(ind in nombre_l for ind in PALABRAS_INDICIO_ESTRUCTURA)
    )
    return es_nombre_persona and tiene_marca_profesion_solo and not tiene_indicio_estructura


def _parece_empresa(nombre: str, zona: str, texto_extra: str = "") -> bool:
    """texto_extra: snippet/descripción/URL — algunos casos reales (homónimos
    de zona en otro país, RUC en vez de CUIT) no se mencionan en el título
    pero sí en el snippet o en la URL (ej. 'FedEx Bella Vista' no dice
    'Arkansas' en el título, pero la URL sí: /es-us/ar/bella-vista)."""
    nombre_l = nombre.strip().lower()
    if not nombre_l:
        return False
    if nombre_l == zona.strip().lower():
        return False  # el título es literalmente el nombre de la zona, no una empresa
    if nombre_l in PALABRAS_GENERICAS_SOLAS:
        return False  # "Empresas", "Contacto", "Inicio"... no es un nombre real
    if any(p.search(nombre_l) for p in _PATRONES_NO_EMPRESA_COMPILADOS):
        return False
    if texto_extra and any(p.search(texto_extra.lower()) for p in _PATRONES_NO_EMPRESA_COMPILADOS):
        return False
    # Nota: se descartó un filtro de "nombre de persona" (2 palabras Capitalizadas)
    # porque atrapaba también nombres reales de empresa de 2 palabras (ej.
    # "Carrefour Argentina"). Un nombre de persona ocasional que se cuele se
    # descarta en la revisión manual del .txt exportado — es más seguro que
    # perder empresas reales con ese patrón.
    return True


def _dominio(url: str) -> str:
    m = re.search(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1).lower() if m else ""


# ccTLDs de países donde Marco no puede trabajar (todo lo que no sea
# Argentina) — encontrado en producción: zonas como "Bella Vista" son
# homónimo de ciudades en EEUU, México, Chile, Perú y Guatemala, y ninguna
# lista fija de dominios alcanza para cubrir eso. Bloquear por ccTLD es
# mucho más robusto que intentar enumerar cada sitio extranjero uno por uno.
TLDS_EXTRANJEROS = (
    ".mx", ".cl", ".pe", ".co", ".gt", ".py", ".uy", ".bo", ".ec", ".cr",
    ".pa", ".do", ".es", ".us", ".br", ".ve", ".hn", ".sv", ".ni",
)

# organismos estatales/gobierno: no son empleadores privados accionables por
# postulación espontánea, el ingreso funciona distinto (concurso público, etc.)
DOMINIOS_GOBIERNO = (".gob.ar", ".gov")


def _es_dominio_excluido(url: str) -> bool:
    """Coincidencia exacta/subdominio para entradas de solo-dominio (nunca
    substring suelto — 'x.com' como substring bloqueaba cualquier dominio
    que terminara en 'x.com...', como 'empresax.com.ar'; bug real encontrado
    en testing). Para entradas que incluyen una ruta (ej. 'facebook.com/photo'),
    se compara contra la URL completa, ya que esas nunca podían matchear
    contra el dominio solo (bug preexistente, separado del anterior)."""
    if not url:
        return False
    dom = _dominio(url)
    url_l = url.lower()
    if dom and dom.endswith(TLDS_EXTRANJEROS):
        return True
    if dom and dom.endswith(DOMINIOS_GOBIERNO):
        return True
    for excl in DOMINIOS_EXCLUIR + DOMINIOS_RUIDO_NO_EMPRESA:
        if "/" in excl:
            if excl.lower() in url_l:
                return True
        elif dom and (dom == excl or dom.endswith("." + excl)):
            return True
    return False


def _limpiar_nombre(titulo: str) -> str:
    nombre = titulo
    for patron in SUFIJOS_A_LIMPIAR:
        nombre = re.sub(patron, "", nombre, flags=re.IGNORECASE)
    return nombre.strip(" -–|")


def _quitar_acentos(texto: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def _normalizar_para_dedupe(nombre: str) -> str:
    # bug real: "Logística" (con tilde) y "Logistica" (sin tilde) son la
    # MISMA palabra, pero sin sacar acentos generaban claves distintas y el
    # motor promovía la misma empresa dos veces solo por esa diferencia.
    n = _quitar_acentos(nombre.lower())
    n = re.sub(r"\b(s\.?a\.?|s\.?r\.?l\.?)\b", "", n)
    n = re.sub(r"[^a-z0-9]+", "", n)
    return n


def extraer_candidatas(resultado_serper: dict, zona: str) -> list[dict]:
    """De un resultado crudo de Serper, extrae candidatas plausibles (heurística)."""
    candidatas = []
    for item in resultado_serper.get("organic", []):
        url = item.get("link", "")
        titulo = item.get("title", "")
        snippet = item.get("snippet", "")
        if not titulo or _es_dominio_excluido(url):
            continue
        nombre = _limpiar_nombre(titulo)
        if len(nombre) < 3 or len(nombre) > 90:
            continue
        if not _parece_empresa(nombre, zona, texto_extra=f"{snippet} {url}"):
            continue
        candidatas.append({"nombre_crudo": nombre, "url": url, "snippet": snippet, "zona": zona})
    return candidatas


def _ya_existe_en_db(nombre: str, conn) -> bool:
    norm = _normalizar_para_dedupe(nombre)
    rows = conn.execute("SELECT nombre FROM companies").fetchall()
    return any(_normalizar_para_dedupe(r["nombre"]) == norm for r in rows)


def _ya_descubierta(nombre: str, zona: str, conn) -> bool:
    norm = _normalizar_para_dedupe(nombre)
    rows = conn.execute("SELECT nombre_crudo FROM discovered_companies_raw WHERE zona=?", (zona,)).fetchall()
    return any(_normalizar_para_dedupe(r["nombre_crudo"]) == norm for r in rows)


def ejecutar_query(query: str, zona: str, tipo: str, keyword: str = "") -> dict:
    """Ejecuta una query, guarda el log, extrae y persiste candidatas nuevas
    (deduplicadas). Devuelve métricas de rendimiento de esta query."""
    conn = get_conn()
    try:
        resultado = search_client.buscar(query)
    except SearchClientError as e:
        # Importante: se registra en queries_log IGUAL que una búsqueda exitosa,
        # aunque haya fallado. Si no se registrara, una falla de red o de API
        # (key sin cupo, timeout) no descontaría nunca del presupuesto por
        # corrida (max_ciclos) y el motor podría reintentar sin parar — pasó
        # en pruebas: con la API caída, el loop se colgaba indefinidamente.
        conn.execute(
            "INSERT INTO queries_log (query, zona, keyword, tipo, resultados, empresas_nuevas, duplicados, yield, creado_en) "
            "VALUES (?, ?, ?, ?, 0, 0, 0, 0, ?)",
            (query, zona, keyword, tipo, now()),
        )
        conn.commit()
        conn.close()
        return {"query": query, "error": str(e), "resultados": 0, "empresas_nuevas": 0}

    # queries_log se inserta ANTES de las candidatas (no después, como estaba):
    # bug real encontrado con datos de producción — se guardaba el query_id
    # recién al final, así que TODAS las candidatas de discovery.py (la fuente
    # paga principal) quedaban con query_id=NULL para siempre. Eso rompía el
    # LEFT JOIN en promote.py (_inferir_rubro no encontraba el keyword de la
    # búsqueda) y toda candidata sin match en el snippet caía al rubro por
    # defecto "logistica", sin importar el rubro real. Se actualiza con las
    # métricas finales (resultados/empresas_nuevas/etc.) al terminar.
    cur = conn.execute(
        "INSERT INTO queries_log (query, zona, keyword, tipo, resultados, empresas_nuevas, duplicados, yield, creado_en) "
        "VALUES (?, ?, ?, ?, 0, 0, 0, 0, ?)",
        (query, zona, keyword, tipo, now()),
    )
    query_id = cur.lastrowid

    crudas = extraer_candidatas(resultado, zona)
    nuevas = 0
    duplicadas = 0
    for c in crudas:
        if _ya_existe_en_db(c["nombre_crudo"], conn) or _ya_descubierta(c["nombre_crudo"], zona, conn):
            duplicadas += 1
            continue
        conn.execute(
            "INSERT INTO discovered_companies_raw (nombre_crudo, url, snippet, zona, query_id, estado, creado_en) "
            "VALUES (?, ?, ?, ?, ?, 'DISCOVERED', ?)",
            (c["nombre_crudo"], c["url"], c["snippet"], zona, query_id, now()),
        )
        nuevas += 1

    total = len(crudas)
    yield_score = round(nuevas / total, 2) if total else 0.0

    conn.execute(
        "UPDATE queries_log SET resultados=?, empresas_nuevas=?, duplicados=?, yield=? WHERE id=?",
        (total, nuevas, duplicadas, yield_score, query_id),
    )

    if keyword:
        conn.execute(
            "INSERT INTO keywords (termino, categoria, queries_usadas, empresas_encontradas, empresas_unicas, yield_score, creado_en) "
            "VALUES (?, 'general', 1, ?, ?, ?, ?) "
            "ON CONFLICT(termino) DO UPDATE SET "
            "queries_usadas = queries_usadas + 1, "
            "empresas_encontradas = empresas_encontradas + excluded.empresas_encontradas, "
            "empresas_unicas = empresas_unicas + excluded.empresas_unicas, "
            "yield_score = (yield_score * (queries_usadas) + excluded.yield_score) / (queries_usadas + 1)",
            (keyword, total, nuevas, yield_score, now()),
        )

    conn.commit()
    conn.close()
    return {"query": query, "resultados": total, "empresas_nuevas": nuevas, "duplicados": duplicadas,
            "yield": yield_score, "query_id": query_id}


def descubrir_zona(zona: str, max_queries: int = 20, pausa_entre_queries: float = 0.3) -> dict:
    """Corre un lote de queries multicapa para una zona, respetando presupuesto.
    Devuelve resumen + detecta si la zona parece saturada (yield bajo sostenido)."""
    todas_keywords = [kw for lista in KEYWORDS_SEED.values() for kw in lista]
    queries = []
    for kw in todas_keywords:
        queries.extend(plantillas_query(zona, kw))
    queries.extend(plantillas_query(zona))  # queries genéricas sin keyword

    ejecutadas = []
    yields_recientes = []
    saturada = False
    for i, q in enumerate(queries[:max_queries]):
        r = ejecutar_query(q["query"], zona, q["tipo"], q.get("keyword", ""))
        ejecutadas.append(r)
        yields_recientes.append(r.get("empresas_nuevas", 0))
        if len(yields_recientes) >= 5 and sum(yields_recientes[-5:]) == 0:
            saturada = True
            break
        time.sleep(pausa_entre_queries)

    total_nuevas = sum(r.get("empresas_nuevas", 0) for r in ejecutadas)
    return {
        "zona": zona, "queries_ejecutadas": len(ejecutadas), "empresas_nuevas": total_nuevas,
        "saturada": saturada, "detalle": ejecutadas,
    }


_PATRONES_FRASE_DESCUBRIBLE = [
    re.compile(r"\b(limpieza|mantenimiento|servicio|distribuci[oó]n|fabricaci[oó]n|producci[oó]n|"
               r"venta|reparaci[oó]n|instalaci[oó]n) de ([a-záéíóúñ]+(?:\s[a-záéíóúñ]+)?)", re.IGNORECASE),
]
MAX_KEYWORDS_DESCUBIERTAS = 300  # tope para no crecer sin límite


_STOPWORDS_FRASE = {"de", "del", "la", "el", "los", "las", "y", "en", "con", "para", "un", "una"}


def extraer_keywords_de_texto(texto: str) -> list[str]:
    """Detecta frases tipo "servicio de X" / "fabricación de X" en la
    descripción de una empresa recién encontrada — el "entramado": una
    búsqueda de limpieza puede traer una empresa cuya descripción menciona
    "limpieza de trenes", término que no estaba en el diccionario semilla y
    que ahora se puede probar por su cuenta en futuras búsquedas."""
    if not texto:
        return []
    hallazgos = []
    for patron in _PATRONES_FRASE_DESCUBRIBLE:
        for m in patron.finditer(texto):
            disparador = m.group(1).lower()
            objeto_palabras = [w for w in m.group(2).lower().split() if w not in _STOPWORDS_FRASE]
            if not objeto_palabras:
                continue  # el "objeto" era solo una stopword (ej. capturó "de" solo), no sirve
            frase = f"{disparador} de {' '.join(objeto_palabras)}"
            if 8 <= len(frase) <= 40:
                hallazgos.append(frase)
    return list(dict.fromkeys(hallazgos))  # dedup preservando orden


def registrar_keyword_descubierta(termino: str, categoria: str = "general"):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO keywords (termino, categoria, origen, creado_en) VALUES (?, ?, 'discovered', ?)",
        (termino, categoria, now()),
    )
    conn.commit()
    conn.close()
