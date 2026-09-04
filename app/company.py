"""Company DNA — ficha estructurada de cada empresa, persistida en SQLite.
Incluye alta, actualización con detección de cambio de score, y consulta why-not.
"""
import json
from dataclasses import dataclass

from app.db import get_conn, now
from app.negative_signals import NegativeSignal, debe_descartar
from app.signals import Signal, hiring_signal_score
from app.scoring import EmployerInputs, JackpotInputs, employer_score, jackpot_score, confidence, Evidencia, chances_de_entrar


def upsert_company(nombre: str, rubro: str, zona: str, localidad: str = "",
                    antiguedad_anios: int | None = None, tamano_estimado: str = "desconocido",
                    actividad: str = "") -> int:
    conn = get_conn()
    row = conn.execute("SELECT id FROM companies WHERE nombre = ?", (nombre,)).fetchone()
    ts = now()
    if row:
        conn.execute(
            "UPDATE companies SET rubro=?, zona=?, localidad=?, antiguedad_anios=?, "
            "tamano_estimado=?, actividad=?, actualizado_en=? WHERE id=?",
            (rubro, zona, localidad, antiguedad_anios, tamano_estimado, actividad, ts, row["id"]),
        )
        company_id = row["id"]
    else:
        cur = conn.execute(
            "INSERT INTO companies (nombre, rubro, zona, localidad, antiguedad_anios, "
            "tamano_estimado, actividad, estado, creado_en, actualizado_en) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 'candidata', ?, ?)",
            (nombre, rubro, zona, localidad, antiguedad_anios, tamano_estimado, actividad, ts, ts),
        )
        company_id = cur.lastrowid
    conn.commit()
    conn.close()
    return company_id


def add_source(company_id: int, url: str, tipo: str = "otro", descripcion: str = "") -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO sources (company_id, url, tipo, descripcion, creado_en) VALUES (?, ?, ?, ?, ?)",
        (company_id, url, tipo, descripcion, now()),
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def add_signal(company_id: int, sig: Signal, fuente_id: int | None = None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO signals (company_id, tipo, fuerza, descripcion, fuente_id, fecha_evento, creado_en) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (company_id, sig.tipo, sig.fuerza, sig.descripcion, fuente_id, sig.fecha_evento, now()),
    )
    conn.commit()
    conn.close()


def add_negative_signal(company_id: int, neg: NegativeSignal, fuente_id: int | None = None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO negative_signals (company_id, tipo, gravedad, vigencia, fecha_evento, fuente_id, descripcion, creado_en) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (company_id, neg.tipo, neg.gravedad, neg.vigencia, neg.fecha_evento, fuente_id, neg.descripcion, now()),
    )
    conn.commit()
    conn.close()


def add_job_hypothesis(company_id: int, puesto: str, probabilidad: int, justificacion: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO job_hypotheses (company_id, puesto, probabilidad, justificacion, creado_en) VALUES (?, ?, ?, ?, ?)",
        (company_id, puesto, probabilidad, justificacion, now()),
    )
    conn.commit()
    conn.close()


def add_cv_match(company_id: int, cv: str, match_score: int, justificacion: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO cv_matches (company_id, cv, match_score, justificacion, creado_en) VALUES (?, ?, ?, ?, ?)",
        (company_id, cv, match_score, justificacion, now()),
    )
    conn.commit()
    conn.close()


def add_transport_access(company_id: int, red: str, tipo: str, minutos_caminata: int,
                          minutos_viaje_total: int, combinaciones: int = 0, fuente: str = ""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO transport_access (company_id, red, tipo, minutos_caminata, minutos_viaje_total, "
        "combinaciones, fuente, creado_en) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (company_id, red, tipo, minutos_caminata, minutos_viaje_total, combinaciones, fuente, now()),
    )
    conn.commit()
    conn.close()


def get_transport_access(company_id: int):
    from app.transport import AccesoTransporte
    conn = get_conn()
    rows = conn.execute("SELECT * FROM transport_access WHERE company_id=?", (company_id,)).fetchall()
    conn.close()
    return [AccesoTransporte(red=r["red"], tipo=r["tipo"], minutos_caminata=r["minutos_caminata"],
                              minutos_viaje_total=r["minutos_viaje_total"], combinaciones=r["combinaciones"],
                              fuente=r["fuente"] or "") for r in rows]


def add_contact(company_id: int, tipo: str, valor: str, verificado: bool, fuente_id: int | None = None,
                 mx_verificado: bool | None = None) -> int:
    """REGLA DURA: solo contacto a nivel empresa. Nunca nombres/emails de personas individuales."""
    if any(kw in valor.lower() for kw in ["gerente", "rrhh -", "sr.", "sra.", "lic. "]):
        raise ValueError("Contacto rechazado: parece referirse a una persona individual, no a la empresa.")
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO contacts (company_id, tipo, valor, verificado, fuente_id, es_persona, mx_verificado, creado_en) "
        "VALUES (?, ?, ?, ?, ?, 0, ?, ?)",
        (company_id, tipo, valor, int(verificado), fuente_id,
         (None if mx_verificado is None else int(mx_verificado)), now()),
    )
    conn.commit()
    conn.close()
    return cur.lastrowid


def get_company(company_id: int) -> dict:
    conn = get_conn()
    company = dict(conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone())
    company["sources"] = [dict(r) for r in conn.execute("SELECT * FROM sources WHERE company_id=?", (company_id,))]
    company["signals"] = [dict(r) for r in conn.execute("SELECT * FROM signals WHERE company_id=?", (company_id,))]
    company["negative_signals"] = [dict(r) for r in conn.execute("SELECT * FROM negative_signals WHERE company_id=?", (company_id,))]
    company["job_hypotheses"] = [dict(r) for r in conn.execute("SELECT * FROM job_hypotheses WHERE company_id=?", (company_id,))]
    company["cv_matches"] = [dict(r) for r in conn.execute("SELECT * FROM cv_matches WHERE company_id=?", (company_id,))]
    company["contacts"] = [dict(r) for r in conn.execute("SELECT * FROM contacts WHERE company_id=?", (company_id,))]
    company["scores"] = [dict(r) for r in conn.execute("SELECT * FROM scores WHERE company_id=? ORDER BY creado_en DESC", (company_id,))]
    conn.close()
    return company


def ultimo_score(company_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM scores WHERE company_id=? ORDER BY creado_en DESC LIMIT 1", (company_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def calcular_y_guardar_score(company_id: int, employer_inputs: EmployerInputs,
                              accessibility: int, contactability: int,
                              evidencias: list[Evidencia],
                              puesto_objetivo: str | None = None,
                              vacante_confirmada: bool = False,
                              sueldo_min: int | None = None, sueldo_max: int | None = None,
                              sueldo_fuente: str | None = None) -> dict:
    """`accessibility` es el fallback geográfico (app.geography); si hay datos de
    transporte cargados (app.transport / add_transport_access), esos reemplazan
    ese valor por un score multimodal real (San Martín + colectivos 182/320/237/463).
    Recalcula todo el pipeline de scoring para una empresa y detecta cambios
    respecto del último score guardado (Change Detection)."""
    from app.transport import transport_access_score, mejor_acceso
    from app.exclusions import es_zona_prohibida

    TOPE_MINUTOS_VIAJE = 50  # regla dura: viaje neto en colectivo/tren, no negociable

    accesos = get_transport_access(company_id)
    viaje_excede_tope = False
    if accesos:
        accessibility = transport_access_score(accesos)
        mejor = mejor_acceso(accesos)
        if mejor and mejor.minutos_viaje_total > TOPE_MINUTOS_VIAJE:
            viaje_excede_tope = True

    conn = get_conn()
    zona_row = conn.execute("SELECT zona FROM companies WHERE id=?", (company_id,)).fetchone()
    zona_prohibida = es_zona_prohibida(zona_row["zona"]) if zona_row else None
    signals_rows = conn.execute("SELECT tipo, fuerza, descripcion FROM signals WHERE company_id=?", (company_id,)).fetchall()
    signals = [Signal(tipo=r["tipo"], fuerza=r["fuerza"], descripcion=r["descripcion"], fuente_url="") for r in signals_rows]
    hs_score = hiring_signal_score(signals)

    negs_rows = conn.execute("SELECT tipo, gravedad, vigencia, descripcion FROM negative_signals WHERE company_id=?", (company_id,)).fetchall()
    negs = [NegativeSignal(tipo=r["tipo"], gravedad=r["gravedad"], vigencia=r["vigencia"], descripcion=r["descripcion"], fuente_url="") for r in negs_rows]
    descartar, motivo = debe_descartar(negs)

    matches_rows = conn.execute("SELECT cv, match_score FROM cv_matches WHERE company_id=?", (company_id,)).fetchall()
    mejor_match = max((r["match_score"] for r in matches_rows), default=0)
    cv_recomendado = None
    if matches_rows:
        cv_recomendado = max(matches_rows, key=lambda r: r["match_score"])["cv"]

    contacts_count = conn.execute("SELECT COUNT(*) c FROM contacts WHERE company_id=? AND verificado=1", (company_id,)).fetchone()["c"]

    emp_score = employer_score(employer_inputs)
    jp_inputs = JackpotInputs(
        employer_quality=emp_score,
        opportunity_match=mejor_match,
        hiring_signals=hs_score,
        accessibility=accessibility,
        contactability=contactability,
    )
    jp_score = jackpot_score(jp_inputs)
    conf = confidence(evidencias, tiene_contacto_verificado=contacts_count > 0,
                       cantidad_fuentes_independientes=len(conn.execute("SELECT id FROM sources WHERE company_id=?", (company_id,)).fetchall()))

    if descartar:
        jp_score = min(jp_score, 30)  # las señales negativas críticas capan el score

    if viaje_excede_tope or zona_prohibida:
        descartar = True
        motivo_viaje = f"Viaje neto supera el tope de {TOPE_MINUTOS_VIAJE} min" if viaje_excede_tope else None
        motivo_zona = f"Zona prohibida: {zona_prohibida}" if zona_prohibida else None
        motivo = " / ".join(m for m in [motivo, motivo_viaje, motivo_zona] if m)
        jp_score = min(jp_score, 10)  # regla dura: no negociable, ni siquiera "en revisión"

    chances, chances_baja_confianza = chances_de_entrar(mejor_match, hs_score, emp_score, vacante_confirmada)
    if descartar:
        chances = min(chances, 15)

    detalle = {
        "hiring_signal_score": hs_score,
        "employer_score": emp_score,
        "opportunity_score": mejor_match,
        "accessibility_score": accessibility,
        "contactability_score": contactability,
        "descartar_por_señal_negativa": descartar,
        "motivo_descarte": motivo,
        "evidencias": [{"afirmacion": e.afirmacion, "nivel": e.nivel} for e in evidencias],
    }

    conn.execute(
        "INSERT INTO scores (company_id, employer_score, hiring_signal_score, opportunity_score, "
        "accessibility_score, contactability_score, jackpot_score, confidence, cv_recomendado, "
        "puesto_objetivo, chances_estimadas, chances_baja_confianza, sueldo_min, sueldo_max, "
        "sueldo_es_estimado, sueldo_fuente, detalle_json, creado_en) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)",
        (company_id, emp_score, hs_score, mejor_match, accessibility, contactability,
         jp_score, conf, cv_recomendado, puesto_objetivo, chances, int(chances_baja_confianza),
         sueldo_min, sueldo_max, sueldo_fuente, json.dumps(detalle, ensure_ascii=False), now()),
    )

    nuevo_estado = "jackpot" if (jp_score >= 90 and not descartar) else (
        "descartada" if descartar else ("en_revision" if jp_score >= 65 else "descartada")
    )
    conn.execute(
        "UPDATE companies SET estado=?, motivo_descarte=?, actualizado_en=? WHERE id=?",
        (nuevo_estado, motivo, now(), company_id),
    )
    conn.commit()
    conn.close()

    return {
        "jackpot_score": jp_score, "confidence": conf, "employer_score": emp_score,
        "hiring_signal_score": hs_score, "opportunity_score": mejor_match,
        "cv_recomendado": cv_recomendado, "estado": nuevo_estado, "detalle": detalle,
    }


def set_direccion_y_geocodificar(company_id: int, direccion: str) -> dict | None:
    """Geocodifica una dirección real (vía OSM Nominatim, gratis) y guarda
    coordenadas + distancia en línea recta desde el domicilio de Marco.
    No calcula tiempo de viaje real (eso requiere un motor de rutas aparte) —
    es un dato objetivo para descartar casos obviamente lejos antes de
    estimar el viaje real a mano con app.transport."""
    from app.geocoding import calcular_distancia_a_empresa
    from app.geography import estacion_mas_cercana
    resultado = calcular_distancia_a_empresa(direccion)
    conn = get_conn()
    if resultado:
        estacion = estacion_mas_cercana(resultado["lat"], resultado["lon"])
        conn.execute(
            "UPDATE companies SET direccion=?, lat=?, lon=?, distancia_km=?, "
            "estacion_cercana=?, estacion_distancia_metros=?, estacion_caminata_min=?, actualizado_en=? WHERE id=?",
            (direccion, resultado["lat"], resultado["lon"], resultado["distancia_km"],
             estacion["estacion"] if estacion else None,
             estacion["distancia_metros"] if estacion else None,
             estacion["minutos_caminata_estimados"] if estacion else None,
             now(), company_id),
        )
        if estacion:
            resultado["estacion_cercana"] = estacion
    else:
        conn.execute("UPDATE companies SET direccion=?, actualizado_en=? WHERE id=?", (direccion, now(), company_id))
    conn.commit()
    conn.close()
    return resultado


def why_not(company_id: int) -> str | None:
    conn = get_conn()
    row = conn.execute("SELECT estado, motivo_descarte, nombre FROM companies WHERE id=?", (company_id,)).fetchone()
    conn.close()
    if row["estado"] != "descartada":
        return None
    return f"{row['nombre']} — DESCARTADA. Motivo: {row['motivo_descarte'] or 'no especificado'}."
