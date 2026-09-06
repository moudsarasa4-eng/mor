"""Exporta las candidatas descubiertas (estado='candidata', todavía no puntuadas)
a un .txt legible en la carpeta Descargas del usuario, para pasarlo a una sesión
de Claude y que haga el análisis real (contacto, seriedad, señales, CV match).

Solo exporta las que no se exportaron todavía (columna exportada_txt), para no
repetir la misma lista larga en cada tanda.
"""
from datetime import date, datetime
from pathlib import Path

from app.db import get_conn

DOWNLOADS_FALLBACK = Path(__file__).resolve().parent.parent / "reports"


def _carpeta_descargas() -> Path:
    descargas = Path.home() / "Downloads"
    if descargas.exists():
        return descargas
    DOWNLOADS_FALLBACK.mkdir(exist_ok=True)
    return DOWNLOADS_FALLBACK


def exportar_candidatas_txt(zona: str | None = None, solo_nuevas: bool = True) -> str | None:
    conn = get_conn()

    query = (
        "SELECT c.id, c.nombre, c.zona, c.rubro, c.actividad, c.distancia_km, c.contacto_intentado_sin_resultado, "
        "c.sueldo_ref_min, c.sueldo_ref_max, c.sueldo_ref_fuente, c.sueldo_ref_confianza, c.origen_contacto, "
        "c.tamano_estimado FROM companies c "
        "WHERE c.estado='candidata' "
        "AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = c.id)"
    )
    params = []
    if solo_nuevas:
        query += " AND c.exportada_txt = 0"
    if zona:
        query += " AND c.zona = ?"
        params.append(zona)
    # los referidos/presenciales van primero (convierten mejor que un
    # hallazgo web frío); los negocios unipersonales/muy chicos van al final
    # (misma zona, pero no se los quiere mezclado con candidatas serias).
    query += " ORDER BY (c.origen_contacto = 'presencial') DESC, (c.tamano_estimado = 'chica') ASC, c.zona, c.id"

    filas = conn.execute(query, params).fetchall()
    if not filas:
        conn.close()
        return None

    lineas = [
        "MOTOR DE JACKPOTS — CANDIDATAS DESCUBIERTAS (sin analizar todavía)",
        f"Generado: {datetime.now().isoformat(timespec='seconds')}",
        f"Total en este archivo: {len(filas)}",
        "",
        "Pegá este archivo completo en una conversación con Claude para que audite cada",
        "empresa (seriedad, señales, contacto, CV match) y genere los emails.",
        "Las marcadas [REFERIDO/PRESENCIAL] van primero: son contactos reales conseguidos",
        "a mano, con mayor probabilidad de conversión que un hallazgo web frío.",
        "=" * 70,
        "",
    ]

    zona_actual = None
    for f in filas:
        if f["zona"] != zona_actual:
            zona_actual = f["zona"]
            lineas.append(f"\n### ZONA: {zona_actual}\n")
        if f["origen_contacto"] == "presencial":
            lineas.append("[REFERIDO/PRESENCIAL]")
        if f["tamano_estimado"] == "chica":
            lineas.append("[NEGOCIO CHICO/UNIPERSONAL — revisar con cautela, puede no tener capacidad de sumar personal]")
        fuente = conn.execute(
            "SELECT url FROM sources WHERE company_id=? ORDER BY id LIMIT 1", (f["id"],)
        ).fetchone()
        contactos = conn.execute(
            "SELECT tipo, valor, mx_verificado FROM contacts WHERE company_id=? ORDER BY id", (f["id"],)
        ).fetchall()
        lineas.append(f"[{f['id']}] {f['nombre']}")
        lineas.append(f"    Rubro estimado: {f['rubro']}")
        if fuente and fuente["url"]:
            lineas.append(f"    Fuente: {fuente['url']}")
        elif f["actividad"] and "OpenStreetMap" in f["actividad"]:
            # bug real: las candidatas de Overpass tienen una fila en `sources`
            # con url=NULL (promote.py inserta la fuente igual, sin URL real
            # porque no viene de una búsqueda web) — "if fuente:" chequeaba
            # solo que la fila existiera, no que tuviera URL, y terminaba
            # imprimiendo literalmente "Fuente: None".
            lineas.append("    Fuente: OpenStreetMap (sin URL — descubierta por ubicación/categoría, no por búsqueda web)")
        if f["actividad"]:
            lineas.append(f"    Descripción: {f['actividad']}")
        if f["distancia_km"] is not None:
            lineas.append(f"    Distancia en línea recta: {f['distancia_km']} km")
        if f["sueldo_ref_min"] is not None:
            rango = f"${f['sueldo_ref_min']:,}–${f['sueldo_ref_max']:,}".replace(",", ".")
            lineas.append(
                f"    Sueldo estimado (por rubro, no específico de esta empresa, confianza {f['sueldo_ref_confianza']}): {rango}"
            )
            # "Fuente del sueldo" (no "Fuente" a secas): reutilizar la misma
            # etiqueta que la fuente de la empresa (línea de arriba) generaba
            # ambigüedad real al leer/parsear el archivo — encontrado
            # auditando con un archivo real, donde una candidata sin fuente
            # propia (ej. de Overpass) terminaba pareciendo tener como
            # "Fuente" el convenio salarial en vez de su origen real.
            lineas.append(f"      Fuente del sueldo: {f['sueldo_ref_fuente']}")
        if contactos:
            for c in contactos:
                mx_txt = ""
                if c["tipo"] == "email":
                    if c["mx_verificado"] == 1:
                        mx_txt = " [dominio con MX OK]"
                    elif c["mx_verificado"] == 0:
                        mx_txt = " [⚠ dominio SIN registro MX — probablemente no recibe mail]"
                lineas.append(f"    Contacto ({c['tipo']}, sin confirmar): {c['valor']}{mx_txt}")
        elif f["contacto_intentado_sin_resultado"]:
            lineas.append("    Contacto: se buscó y no se encontró ningún email/teléfono público (revisar el sitio a mano)")
        else:
            lineas.append("    Contacto: no encontrado todavía (correr 'find-contacts')")
        lineas.append("")

    contenido = "\n".join(lineas)
    carpeta = _carpeta_descargas()
    nombre_archivo = f"motor_jackpots_candidatas_{date.today().isoformat()}_{datetime.now().strftime('%H%M%S')}.txt"
    ruta = carpeta / nombre_archivo
    ruta.write_text(contenido, encoding="utf-8")

    ids = [f["id"] for f in filas]
    conn.executemany("UPDATE companies SET exportada_txt=1 WHERE id=?", [(i,) for i in ids])
    conn.commit()
    conn.close()

    return str(ruta)
