"""Triage automático — el multiplicador del motor.

El motor descubre miles de candidatas pero puntuar cada una (jackpot_score,
cv_match, señales) es trabajo manual/de Claude. Resultado: montañas de
candidatas sin ordenar. Este módulo calcula un PRE-SCORE 0-100 para CADA
candidata usando SOLO datos que ya están en la base (rubro, texto ya
descargado, reseñas de dir.ar, sitio activo, distancia geocodificada,
contacto) — sin gastar una sola búsqueda de Serper — para que la revisión
humana empiece por las 30-50 mejores en vez de por las 1778 en orden crudo.

IMPORTANTE — qué NO es esto:
- NO es el jackpot_score verificado. Ese vive en la tabla `scores` + el
  `estado` de la empresa, y requiere verificación real (humano/Claude).
- Este triage NUNCA cambia el estado de una candidata a 'jackpot'. Solo
  escribe `triage_score` para ordenarlas. Una candidata con triage 95 sigue
  siendo 'candidata' hasta que alguien la verifique de verdad.
- Toda la evidencia que usa es INFERIDA de texto ya descargado; nunca
  inventa datos (regla dura del proyecto). Las señales y contactos que mina
  quedan marcados con procedencia "[auto/snippet]" para que se sepa que no
  fueron verificados a mano.
"""
import json

from app.db import get_conn, now
from app.snippet_mining import minar_texto
from app.signals import Signal, clasificar_fuerza, hiring_signal_score
from app.geography import accessibility_score
from app.promote import _KEYWORD_A_CATEGORIA
from app.keywords import KEYWORDS_SEED

# rubro de la candidata -> CV de Marco. Los 4 rubros del motor mapean 1:1 a
# los 4 CVs, así que toda candidata bien clasificada tiene un CV aplicable.
_RUBRO_A_CV = {
    "logistica": "logistica", "limpieza": "limpieza",
    "administrativo": "administrativo", "atencion_cliente": "atencion_cliente",
}

_PESOS_TRIAGE = {
    "oportunidad": 0.30,   # ¿el rubro/texto matchea un CV de Marco?
    "senales": 0.25,       # ¿hay señales de contratación en el texto?
    "empleador": 0.25,     # proxies de calidad (formalidad, tamaño, reseñas, antigüedad)
    "accesibilidad": 0.10, # geografía (transporte)
    "contactabilidad": 0.10,  # ¿hay algún contacto ya?
}


def _texto_candidata(conn, company_id: int, actividad: str) -> str:
    """Junta TODO el texto ya descargado de una candidata: su actividad, los
    snippets crudos de discovery, y las descripciones de sus fuentes."""
    partes = [actividad or ""]
    for r in conn.execute(
        "SELECT snippet FROM discovered_companies_raw WHERE company_id=? AND snippet IS NOT NULL", (company_id,)
    ):
        partes.append(r["snippet"] or "")
    for r in conn.execute(
        "SELECT descripcion FROM sources WHERE company_id=? AND descripcion IS NOT NULL", (company_id,)
    ):
        partes.append(r["descripcion"] or "")
    return " \n".join(p for p in partes if p)


def _score_oportunidad(rubro: str, texto: str) -> int:
    """Base por rubro→CV (todos los rubros del motor aplican a un CV de Marco)
    + bonus por cuántas keywords de ese CV aparecen literalmente en el texto."""
    if rubro not in _RUBRO_A_CV:
        return 40  # rubro raro: aplica algún CV pero con menos certeza
    from app.snippet_mining import _sin_acentos
    t = _sin_acentos(texto)
    terminos = KEYWORDS_SEED.get(rubro, [])
    hits = sum(1 for kw in terminos if _sin_acentos(kw) in t)
    return min(100, 55 + hits * 8)


def _score_empleador(proxies: dict, tamano_estimado: str | None, sitio_activo) -> int:
    """Proxies observables → 0-100. Conservador: arranca en 40 (neutro) y
    sube/baja con señales concretas."""
    score = 40
    if proxies.get("formalidad_hint"):
        score += 12
    tam = proxies.get("tamano_hint") or tamano_estimado
    if tam == "grande":
        score += 20
    elif tam in ("chica", "unipersonal"):
        score -= 15
    resenas = proxies.get("resenas")
    if resenas:
        try:
            rating = float(proxies.get("rating", 0))
        except ValueError:
            rating = 0
        # muchas reseñas + buen rating = negocio establecido y serio
        if resenas >= 20 and rating >= 4.0:
            score += 18
        elif resenas >= 5:
            score += 8
    if proxies.get("desde_anio"):
        score += 8
    elif proxies.get("anios_trayectoria", 0) >= 10:
        score += 8
    if sitio_activo == 1:
        score += 8
    elif sitio_activo == 0:
        score -= 10
    return max(0, min(100, score))


def _persistir_hallazgos(conn, company_id: int, minado: dict):
    """Escribe señales y contactos minados en la DB (dedup, procedencia clara).
    Nunca inventa: solo lo que estaba literalmente en el texto."""
    # señales — dedup por (company_id, tipo) con marca [auto/snippet]
    existentes = {r["tipo"] for r in conn.execute(
        "SELECT tipo FROM signals WHERE company_id=?", (company_id,))}
    for tipo in minado["senales"]:
        if tipo in existentes:
            continue
        conn.execute(
            "INSERT INTO signals (company_id, tipo, fuerza, descripcion, creado_en) VALUES (?, ?, ?, ?, ?)",
            (company_id, tipo, clasificar_fuerza(tipo),
             "[auto/snippet] detectada en texto ya descargado (sin verificar a mano)", now()),
        )
    # contactos — dedup por valor, verificado=0 (viene de snippet)
    ya = {r["valor"] for r in conn.execute("SELECT valor FROM contacts WHERE company_id=?", (company_id,))}
    for email in minado["contactos"]["emails"]:
        if email in ya:
            continue
        conn.execute(
            "INSERT INTO contacts (company_id, tipo, valor, verificado, es_persona, creado_en) "
            "VALUES (?, 'email', ?, 0, 0, ?)", (company_id, email, now()))
        ya.add(email)
    for tel in minado["contactos"]["telefonos"]:
        if tel in ya:
            continue
        conn.execute(
            "INSERT INTO contacts (company_id, tipo, valor, verificado, es_persona, creado_en) "
            "VALUES (?, 'telefono', ?, 0, 0, ?)", (company_id, tel, now()))
        ya.add(tel)


def triage_candidatas(zona: str | None = None, limite: int | None = None,
                       solo_sin_triage: bool = False) -> dict:
    """Calcula triage_score para candidatas (estado='candidata', sin outreach).
    Mina el texto ya descargado (señales/contactos/proxies), lo persiste, y
    puntúa. NO cambia el estado ni gasta Serper. Idempotente.

    solo_sin_triage=True: solo las que todavía no tienen triage (las recién
    promovidas) — lo que usa el loop automático cada tanda, para no
    recalcular las 1778 cada hora. El comando manual recalcula todo."""
    conn = get_conn()
    query = (
        "SELECT id, nombre, rubro, zona, actividad, tamano_estimado, sitio_activo, distancia_km "
        "FROM companies "
        "WHERE estado='candidata' AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = companies.id)"
    )
    params = []
    if solo_sin_triage:
        query += " AND triage_score IS NULL"
    if zona:
        query += " AND zona = ?"
        params.append(zona)
    query += " ORDER BY id"
    if limite:
        query += f" LIMIT {int(limite)}"
    filas = conn.execute(query, params).fetchall()

    procesadas = 0
    for f in filas:
        cid = f["id"]
        texto = _texto_candidata(conn, cid, f["actividad"] or "")
        minado = minar_texto(texto)
        _persistir_hallazgos(conn, cid, minado)

        tiene_contacto = conn.execute(
            "SELECT 1 FROM contacts WHERE company_id=? LIMIT 1", (cid,)).fetchone() is not None

        signals = [Signal(tipo=t, fuerza=clasificar_fuerza(t), descripcion="", fuente_url="")
                   for t in minado["senales"]]
        s_oportunidad = _score_oportunidad(f["rubro"], texto)
        s_senales = hiring_signal_score(signals)
        s_empleador = _score_empleador(minado["proxies"], f["tamano_estimado"], f["sitio_activo"])
        s_acces = accessibility_score(f["zona"])
        s_contacto = 100 if tiene_contacto else 0

        triage = round(
            s_oportunidad * _PESOS_TRIAGE["oportunidad"]
            + s_senales * _PESOS_TRIAGE["senales"]
            + s_empleador * _PESOS_TRIAGE["empleador"]
            + s_acces * _PESOS_TRIAGE["accesibilidad"]
            + s_contacto * _PESOS_TRIAGE["contactabilidad"]
        )

        detalle = {
            "oportunidad": s_oportunidad, "senales": s_senales, "empleador": s_empleador,
            "accesibilidad": s_acces, "contactabilidad": s_contacto,
            "senales_detectadas": minado["senales"],
            "proxies": minado["proxies"],
            "nota": "PRE-SCORE automático solo para ordenar la revisión — NO es jackpot verificado",
        }
        conn.execute(
            "UPDATE companies SET triage_score=?, triage_detalle=?, triage_en=?, "
            "snippet_minado_en=?, auto_evaluada=1, actualizado_en=? WHERE id=?",
            (triage, json.dumps(detalle, ensure_ascii=False), now(), now(), now(), cid),
        )
        procesadas += 1

    conn.commit()
    conn.close()
    return {"evaluadas": len(filas), "procesadas": procesadas}


def ranking_triage(zona: str | None = None, limite: int = 50) -> list[dict]:
    """Top candidatas por triage_score, para revisión priorizada."""
    conn = get_conn()
    query = (
        "SELECT id, nombre, rubro, zona, triage_score, triage_detalle "
        "FROM companies WHERE estado='candidata' AND triage_score IS NOT NULL"
    )
    params = []
    if zona:
        query += " AND zona = ?"
        params.append(zona)
    query += " ORDER BY triage_score DESC, id DESC LIMIT ?"
    params.append(limite)
    filas = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(f) for f in filas]
