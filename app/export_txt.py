"""Exporta las candidatas descubiertas (estado='candidata', todavía no puntuadas)
a un .txt legible en la carpeta Descargas del usuario, para pasarlo a una sesión
de Claude y que haga el análisis real (contacto, seriedad, señales, CV match).

Solo exporta las que no se exportaron todavía (columna exportada_txt), para no
repetir la misma lista larga en cada tanda.
"""
import sqlite3
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


def _asegurar_columna_exportada(conn):
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN exportada_txt INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass


def exportar_candidatas_txt(zona: str | None = None, solo_nuevas: bool = True) -> str | None:
    conn = get_conn()
    _asegurar_columna_exportada(conn)
    conn.commit()

    query = "SELECT c.id, c.nombre, c.zona, c.rubro, c.actividad FROM companies c WHERE c.estado='candidata'"
    params = []
    if solo_nuevas:
        query += " AND c.exportada_txt = 0"
    if zona:
        query += " AND c.zona = ?"
        params.append(zona)
    query += " ORDER BY c.zona, c.id"

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
        "=" * 70,
        "",
    ]

    zona_actual = None
    for f in filas:
        if f["zona"] != zona_actual:
            zona_actual = f["zona"]
            lineas.append(f"\n### ZONA: {zona_actual}\n")
        fuente = conn.execute(
            "SELECT url FROM sources WHERE company_id=? ORDER BY id LIMIT 1", (f["id"],)
        ).fetchone()
        lineas.append(f"[{f['id']}] {f['nombre']}")
        lineas.append(f"    Rubro estimado: {f['rubro']}")
        if fuente:
            lineas.append(f"    Fuente: {fuente['url']}")
        if f["actividad"]:
            lineas.append(f"    Descripción: {f['actividad']}")
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
