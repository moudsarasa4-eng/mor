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
]
_PATRONES_NO_EMPRESA_COMPILADOS = [re.compile(p, re.IGNORECASE) for p in PATRONES_NO_EMPRESA]


def _parece_empresa(nombre: str, zona: str) -> bool:
    nombre_l = nombre.strip().lower()
    if not nombre_l:
        return False
    if nombre_l == zona.strip().lower():
        return False  # el título es literalmente el nombre de la zona, no una empresa
    if any(p.search(nombre_l) for p in _PATRONES_NO_EMPRESA_COMPILADOS):
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


def _normalizar_para_dedupe(nombre: str) -> str:
    n = nombre.lower()
    n = re.sub(r"\b(s\.?a\.?|s\.?r\.?l\.?)\b", "", n)
    n = re.sub(r"[^a-z0-9áéíóúñ]+", "", n)
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
        if not _parece_empresa(nombre, zona):
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

    crudas = extraer_candidatas(resultado, zona)
    nuevas = 0
    duplicadas = 0
    for c in crudas:
        if _ya_existe_en_db(c["nombre_crudo"], conn) or _ya_descubierta(c["nombre_crudo"], zona, conn):
            duplicadas += 1
            continue
        conn.execute(
            "INSERT INTO discovered_companies_raw (nombre_crudo, url, snippet, zona, estado, creado_en) "
            "VALUES (?, ?, ?, ?, 'DISCOVERED', ?)",
            (c["nombre_crudo"], c["url"], c["snippet"], zona, now()),
        )
        nuevas += 1

    total = len(crudas)
    yield_score = round(nuevas / total, 2) if total else 0.0

    cur = conn.execute(
        "INSERT INTO queries_log (query, zona, keyword, tipo, resultados, empresas_nuevas, duplicados, yield, creado_en) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (query, zona, keyword, tipo, total, nuevas, duplicadas, yield_score, now()),
    )
    query_id = cur.lastrowid

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
