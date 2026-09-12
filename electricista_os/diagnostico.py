"""Motor de diagnóstico determinístico (mismo criterio que el frontend).

Clasifica el texto del cliente por sinónimos, detecta emergencia, arma el
diagnóstico y los escenarios de presupuesto A/B/C a partir del catálogo.
"""
import unicodedata
from .catalogo import (CATALOGO_POR_RANK, SPEECH_POR_RANK, SPEECHS,
                       EMERGENCIA_CLAVES, CLASIFICADOR, FALLAS)


def normalizar(s: str) -> str:
    s = (s or "").lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s


def clasificar(texto: str) -> dict:
    t = normalizar(texto)
    emergencia = any(normalizar(k) in t for k in EMERGENCIA_CLAVES)
    match = None
    for c in CLASIFICADOR:
        if any(normalizar(k) in t for k in c["claves"]):
            match = c
            break
    # En emergencia nunca es un pedido de instalación: si no es una falla, tratarlo como tal.
    if emergencia and (not match or match["rank"] not in FALLAS):
        match = {"rank": 1, "urg": "EMERGENCIA"}
    urg = "EMERGENCIA" if emergencia else (match["urg"] if match else "BAJA")
    return {"emergencia": emergencia, "rank": match["rank"] if match else None, "urgencia": urg}


def _escenarios_desde_rango(mn, mx, precio_visita=40000):
    """A/B/C a partir del rango de precio del trabajo. Nunca inventa si es s/d."""
    if mn is None:
        base = precio_visita
        return [
            {"opcion": "A_BASICO", "titulo": "Básico", "total_estimado": round(base),
             "descripcion": "Solución puntual (estimado — este trabajo no tiene precio de referencia público)."},
            {"opcion": "B_RECOMENDADO", "titulo": "Recomendado", "total_estimado": round(base * 1.6),
             "descripcion": "Solución + revisión relacionada.", "nota_legal": "Precio a confirmar en la visita."},
            {"opcion": "C_COMPLETO", "titulo": "Completo", "total_estimado": round(base * 2.4),
             "descripcion": "Deja la instalación al día."},
        ]
    mx = mx if mx is not None else mn
    medio = (mn + mx) / 2
    return [
        {"opcion": "A_BASICO", "titulo": "Básico", "total_estimado": round(mn),
         "descripcion": "Soluciona el problema puntual."},
        {"opcion": "B_RECOMENDADO", "titulo": "Recomendado", "total_estimado": round(medio),
         "descripcion": "Soluciona el problema + corrige lo relacionado que se detecte."},
        {"opcion": "C_COMPLETO", "titulo": "Completo", "total_estimado": round(mx),
         "descripcion": "Además deja la instalación al día (diferencial / puesta a tierra según corresponda)."},
    ]


def procesar(texto: str, precio_visita=40000) -> dict:
    """Devuelve {diagnostico, escenarios, urgencia, riesgo_tablero, rango, rank}."""
    info = clasificar(texto)
    rank = info["rank"]
    trabajo = CATALOGO_POR_RANK.get(rank) if rank else None
    speech = SPEECH_POR_RANK.get(rank) if rank else None
    if trabajo:
        confianza = 85 if info["emergencia"] else 70
        problema = trabajo["n"]
        rango = f"{trabajo['mn']}-{trabajo['mx']}" if trabajo["mn"] is not None else ""
        escenarios = _escenarios_desde_rango(trabajo["mn"], trabajo["mx"], precio_visita)
        causas = [{"descripcion": f"Compatible con: {trabajo['n']}", "plausibilidad": "ALTA"}]
    else:
        confianza = 40
        problema = "Sin clasificar en la biblioteca de problemas"
        rango = ""
        escenarios = _escenarios_desde_rango(None, None, precio_visita)
        causas = []
    preguntas = speech["preguntas"] if speech else [
        "¿El problema es en toda la casa o en una zona puntual?",
        "¿Notás olor a quemado, chispas o algo caliente?",
        "¿Desde cuándo pasa?",
    ]
    diagnostico = {
        "problema_nombre": problema,
        "confianza_clasificacion": confianza,
        "causas_posibles": causas,
        "preguntas_pendientes": preguntas,
        "urgencia": info["urgencia"],
    }
    return {
        "diagnostico": diagnostico,
        "escenarios": escenarios,
        "urgencia": "CRITICA" if info["urgencia"] == "EMERGENCIA" else info["urgencia"],
        "riesgo_tablero": rank in (2, 3, 17, 19) if rank else False,
        "rango": rango,
        "rank": rank,
    }


def escenarios_publicos() -> list:
    """Lista para la pestaña Escenarios del dashboard."""
    out = []
    for s in SPEECHS:
        out.append({
            "id": str(s["rank"]),
            "nombre": s["nombre"],
            "es_urgencia_critica": s["rank"] == 1,
        })
    return out


def build_prompt(escenario_id: str, texto_cliente: str) -> str:
    speech = SPEECH_POR_RANK.get(int(escenario_id)) if str(escenario_id).isdigit() else None
    trabajo = CATALOGO_POR_RANK.get(int(escenario_id)) if str(escenario_id).isdigit() else None
    nombre = speech["nombre"] if speech else "consulta general"
    preguntas = "\n".join(f"- {q}" for q in (speech["preguntas"] if speech else []))
    upsells = "\n".join(f"- {u}" for u in (speech["upsells"] if speech else []))
    rango = ""
    if trabajo and trabajo["mn"] is not None:
        rango = f"\nRango de referencia de mercado: ${trabajo['mn']:,} – ${trabajo['mx'] or trabajo['mn']:,} (ARS).".replace(",", ".")
    return (
        f"Sos el asistente de Electricista OS (Marco, electricista matriculado, GBA Oeste).\n"
        f"Escenario: {nombre}.{rango}\n\n"
        f"Mensaje del cliente:\n\"{texto_cliente}\"\n\n"
        f"1) Clasificá el problema y estimá urgencia (BAJA/MEDIA/ALTA/CRÍTICA — crítica solo si hay riesgo real).\n"
        f"2) Hacé estas preguntas de calificación si falta info:\n{preguntas or '- (según el caso)'}\n"
        f"3) Sugerí UN upsell relevante (nunca presionar; en emergencia solo seguridad). Opciones:\n{upsells or '- (según diagnóstico)'}\n"
        f"Devolveme una respuesta breve y clara para mandar por WhatsApp, en español rioplatense."
    )
