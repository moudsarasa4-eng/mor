"""Minería de texto YA descargado (snippet + actividad + descripciones de
sources) — extrae señales de contratación, contactos y proxies de calidad de
empleador SIN gastar una sola búsqueda de Serper. Todo esto ya se pagó cuando
se descubrió la candidata; acá se aprovecha lo que estaba tirado.

Regla dura respetada: NO inventa nada. Solo reporta lo que aparece
literalmente en el texto. Un email que está en el snippet es real; una señal
"ampliación" es real si esa palabra está escrita. Nada se deduce de la nada.

Funciones puras (sin I/O, sin red) para poder testear sin base ni internet —
el módulo app.auto_triage las orquesta contra la DB.
"""
import re
import unicodedata


def _sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto or "") if not unicodedata.combining(c)).lower()


# ---------------------------------------------------------------------------
# Señales de contratación / crecimiento (mapea a los tipos de app.signals)
# ---------------------------------------------------------------------------
# frase (sin acentos) -> tipo de señal de app.signals.SEÑALES_*
_PATRONES_SEÑAL = [
    (r"nueva planta|nueva fabrica|inauguracion de planta", "nueva_planta"),
    (r"nueva sucursal|abrimos|inauguramos|nueva tienda|nuevo local", "nueva_sucursal"),
    (r"ampliacion|ampliamos|ampliar|expansion|expandimos", "ampliacion"),
    (r"invers[ai]on|invertir|invertimos", "inversion"),
    (r"aumento de produccion|mayor produccion|aumentamos la produccion", "aumento_produccion"),
    (r"nueva linea|nueva planta productiva|nueva linea de produccion", "nueva_linea_productiva"),
    (r"nueva maquinaria|incorporamos maquinaria|nuevo equipamiento", "incorporacion_maquinaria"),
    (r"nuevo deposito|ampliacion logistica|nuevo centro de distribucion|nuevo centro logistico", "expansion_logistica"),
    (r"sumate al equipo|unite al equipo|busca(?:mos)? personal|busca(?:mos)? empleados|"
     r"incorporamos personal|sumamos personal|"
     r"busqueda laboral|nos encontramos en la busqueda|estamos buscando|"
     r"trabaja con nosotros|forma parte de nuestro equipo|oportunidad laboral|"
     r"sumamos gente|incorporacion de personal|se necesita personal|se busca personal", "contratacion_reciente_similar"),
    (r"mudanza|nos mudamos|nueva direccion|nuevo domicilio", "mudanza_parque_industrial"),
    (r"crecimiento|estamos creciendo|en crecimiento", "crecimiento_operaciones"),
]

# proxies de calidad de empleador (formalidad / tamaño / antigüedad)
_ANTIGUEDAD_RE = re.compile(r"desde (?:el a[nñ]o )?(19\d{2}|20[0-2]\d)|(\d{1,3})\s*a[nñ]os de (?:experiencia|trayectoria)")
_TAMANO_GRANDE_RE = re.compile(r"lider|l[ií]der|multinacional|grupo empresario|m[aá]s de \d{2,} empleados|planta industrial|casa central|sucursales en todo")
_TAMANO_CHICA_RE = re.compile(r"emprendimiento|unipersonal|profesional independiente|a domicilio para particulares")
_FORMALIDAD_RE = re.compile(r"s\.?a\.?\b|s\.?r\.?l\.?\b|cuit|razon social|factura|habilitad[ao]")

# reseñas (vienen del snippet de dir.ar: "4.6★ (80 reseñas)")
_RESENAS_RE = re.compile(r"([\d,\.]+)\s*★\s*\((\d+)\s*rese")

# contacto
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# dos formatos: (a) con código de área (011 4665-1605, +54 11..., 0220...),
# (b) el formato local corto de 8 dígitos con separador (4665-1605), muy
# común en el conurbano oeste donde se escribe el número sin el prefijo.
TEL_RE = re.compile(
    r"(?:\+?54\s?)?(?:0?11|0?[2-9]\d{1,3})[\s.\-]?\d{3,4}[\s.\-]?\d{4}"
    r"|\b\d{4}[\s.\-]\d{4}\b"
)
_EMAILS_RUIDO = ["ejemplo.com", "sentry.io", "wixpress.com", "godaddy.com", "cloudflare.com",
                 "example.com", "email.com", "dominio.com", "tucorreo", "empresa.com"]


def extraer_senales(texto: str) -> list[str]:
    """Tipos de señal de contratación/crecimiento presentes literalmente en el
    texto (deduplicados, en orden de aparición del patrón)."""
    t = _sin_acentos(texto)
    encontradas = []
    for patron, tipo in _PATRONES_SEÑAL:
        if re.search(patron, t) and tipo not in encontradas:
            encontradas.append(tipo)
    return encontradas


def extraer_contactos(texto: str) -> dict:
    """Emails y teléfonos que aparecen literalmente en el texto (filtrando
    ruido genérico de plataformas). Nunca inventa: solo lo escrito."""
    # .rstrip(".,;:") — la regex captura el punto/coma final de "info@x.com. Desde..."
    emails = [e.rstrip(".,;:)") for e in EMAIL_RE.findall(texto or "")
              if not any(r in e.lower() for r in _EMAILS_RUIDO)]
    telefonos = [t.strip() for t in TEL_RE.findall(texto or "")]
    # dedup preservando orden
    emails = list(dict.fromkeys(emails))
    telefonos = list(dict.fromkeys(telefonos))
    return {"emails": emails, "telefonos": telefonos}


def extraer_proxies_calidad(texto: str) -> dict:
    """Proxies OBSERVABLES de calidad de empleador, para alimentar el triage.
    Devuelve señales inferidas, nunca hechos confirmados."""
    t = _sin_acentos(texto)
    proxies = {}

    m = _RESENAS_RE.search(texto or "")
    if m:
        proxies["rating"] = m.group(1).replace(",", ".")
        proxies["resenas"] = int(m.group(2))

    m = _ANTIGUEDAD_RE.search(t)
    if m:
        if m.group(1):
            proxies["desde_anio"] = int(m.group(1))
        elif m.group(2):
            proxies["anios_trayectoria"] = int(m.group(2))

    if _TAMANO_GRANDE_RE.search(t):
        proxies["tamano_hint"] = "grande"
    elif _TAMANO_CHICA_RE.search(t):
        proxies["tamano_hint"] = "chica"

    proxies["formalidad_hint"] = bool(_FORMALIDAD_RE.search(t))
    return proxies


def minar_texto(texto: str) -> dict:
    """Todo junto: señales + contactos + proxies de un bloque de texto."""
    return {
        "senales": extraer_senales(texto),
        "contactos": extraer_contactos(texto),
        "proxies": extraer_proxies_calidad(texto),
    }
