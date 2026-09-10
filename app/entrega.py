"""Entrega de datos: convierte las candidatas de la base en la lista accionable
"a quién le escribo hoy, y por dónde".

Es la única fuente de verdad de esa lista: la usan el dashboard web
(/api/candidatas, /api/entrega.md) y la exportación a Markdown. Antes cada uno
armaba su propia consulta y mostraba cosas distintas — el dashboard ni siquiera
mostraba la página web de la empresa, que es el dato que más falta hacía.

No inventa nada: el sitio sale de `companies.dominio` (ya filtrado de
directorios) y los contactos de la tabla `contacts`.
"""
from datetime import date, datetime
from pathlib import Path

from app.db import get_conn

RUBRO_LEGIBLE = {
    "logistica": "Logística / depósito",
    "limpieza": "Limpieza / mantenimiento",
    "administrativo": "Administrativo",
    "atencion_cliente": "Atención al cliente",
}


def _sitio(dominio: str | None) -> str | None:
    if not dominio:
        return None
    return dominio if dominio.startswith("http") else f"https://{dominio}"


def filas_entrega(zona: str | None = None, rubro: str | None = None,
                  busqueda: str | None = None, solo_contactables: bool = False,
                  minimo_triage: int | None = None, limite: int = 50,
                  offset: int = 0) -> dict:
    """Candidatas listas para contactar, ordenadas por prioridad de revisión.

    solo_contactables: deja solo las que tienen alguna vía real de contacto
    (email, teléfono o sitio propio) — el resto no se puede accionar hoy.
    Devuelve {'total', 'items'} para poder paginar sin recontar a mano.
    """
    conn = get_conn()
    where = ["c.estado='candidata'",
             "NOT EXISTS (SELECT 1 FROM outreach o WHERE o.company_id = c.id)"]
    params: list = []
    if zona:
        where.append("c.zona = ?")
        params.append(zona)
    if rubro:
        where.append("c.rubro = ?")
        params.append(rubro)
    if busqueda:
        where.append("(LOWER(c.nombre) LIKE ? OR LOWER(c.localidad) LIKE ?)")
        like = f"%{busqueda.lower()}%"
        params += [like, like]
    if minimo_triage is not None:
        where.append("c.triage_score >= ?")
        params.append(minimo_triage)
    if solo_contactables:
        where.append("((c.dominio IS NOT NULL AND c.dominio != '') "
                     "OR EXISTS (SELECT 1 FROM contacts ct WHERE ct.company_id = c.id))")
    filtro = " AND ".join(where)

    total = conn.execute(f"SELECT COUNT(*) c FROM companies c WHERE {filtro}", params).fetchone()["c"]
    filas = conn.execute(
        f"""SELECT c.id, c.nombre, c.zona, c.localidad, c.rubro, c.dominio, c.triage_score,
                   c.distancia_km, c.origen_contacto, c.tamano_estimado, c.actividad,
                   c.sueldo_ref_min, c.sueldo_ref_max, c.sueldo_ref_confianza,
                   c.contacto_intentado_sin_resultado,
                   (SELECT url FROM sources s WHERE s.company_id=c.id AND s.url IS NOT NULL
                     ORDER BY s.id LIMIT 1) as fuente
            FROM companies c WHERE {filtro}
            ORDER BY (c.origen_contacto = 'presencial') DESC,
                     c.triage_score DESC NULLS LAST, c.id DESC
            LIMIT ? OFFSET ?""",
        params + [limite, offset],
    ).fetchall()

    items = []
    for f in filas:
        d = dict(f)
        contactos = conn.execute(
            "SELECT tipo, valor, mx_verificado FROM contacts WHERE company_id=? ORDER BY id",
            (f["id"],),
        ).fetchall()
        d["emails"] = [c["valor"] for c in contactos if c["tipo"] == "email"]
        d["telefonos"] = [c["valor"] for c in contactos if c["tipo"] == "telefono"]
        d["emails_sin_mx"] = [c["valor"] for c in contactos
                              if c["tipo"] == "email" and c["mx_verificado"] == 0]
        d["sitio"] = _sitio(f["dominio"])
        d["rubro_legible"] = RUBRO_LEGIBLE.get(f["rubro"], f["rubro"] or "sin clasificar")
        if f["sueldo_ref_min"] is not None:
            d["sueldo"] = f"${f['sueldo_ref_min']:,}-${f['sueldo_ref_max']:,}".replace(",", ".")
        else:
            d["sueldo"] = "No estimable"
        d["via_contacto"] = ("email" if d["emails"] else
                             "telefono" if d["telefonos"] else
                             "web" if d["sitio"] else "presencial")
        items.append(d)

    conn.close()
    return {"total": total, "items": items}


def _celda(valores: list[str], vacio: str = "—") -> str:
    return "<br>".join(valores) if valores else vacio


def render_md(items: list[dict], total: int, titulo_extra: str = "") -> str:
    """Markdown listo para pegar en cualquier lado: una tabla por zona, con
    la página web y la vía de contacto de cada empresa."""
    lineas = [
        "# Empresas para contactar — Motor de Jackpots",
        "",
        f"Generado: {datetime.now().isoformat(timespec='minutes')}  ",
        f"Mostrando **{len(items)}** de **{total}** candidatas sin contactar todavía"
        + (f" · {titulo_extra}" if titulo_extra else ""),
        "",
        "> **Triage** es un pre-score automático 0-100 calculado con datos ya descargados,",
        "> solo para ordenar por dónde empezar. **No** es un jackpot verificado: antes de",
        "> escribir, mirá el sitio y confirmá que la empresa existe y encaja.",
        "",
    ]
    if not items:
        lineas.append("_No hay candidatas que cumplan el filtro._")
        return "\n".join(lineas)

    por_zona: dict[str, list[dict]] = {}
    for it in items:
        por_zona.setdefault(it["zona"] or "Sin zona", []).append(it)

    for zona, filas in por_zona.items():
        lineas += [f"## {zona} ({len(filas)})", ""]
        lineas.append("| Triage | Empresa | Rubro | Página web | Email | Teléfono |")
        lineas.append("|---:|---|---|---|---|---|")
        for f in filas:
            sitio = f"[{f['dominio']}]({f['sitio']})" if f["sitio"] else "—"
            nombre = f["nombre"].replace("|", "/")
            if f["origen_contacto"] == "presencial":
                nombre = f"{nombre} _(referido/presencial)_"
            triage = f["triage_score"] if f["triage_score"] is not None else "—"
            lineas.append(
                f"| {triage} | {nombre} | {f['rubro_legible']} | {sitio} | "
                f"{_celda(f['emails'])} | {_celda(f['telefonos'])} |"
            )
        lineas.append("")

    sin_via = [f for f in items if f["via_contacto"] == "presencial"]
    if sin_via:
        lineas += [
            "---",
            "",
            f"**{len(sin_via)} sin ninguna vía online encontrada** — candidatas para la ronda",
            "presencial (`python main.py ronda-presencial`), que históricamente convierte mejor.",
            "",
        ]
    return "\n".join(lineas)


def _carpeta_descargas() -> Path:
    descargas = Path.home() / "Downloads"
    if descargas.exists():
        return descargas
    fallback = Path(__file__).resolve().parent.parent / "reports"
    fallback.mkdir(exist_ok=True)
    return fallback


def exportar_candidatas_md(zona: str | None = None, limite: int = 300,
                           solo_contactables: bool = True) -> str | None:
    """Escribe el .md en Descargas y devuelve la ruta (None si no hay nada)."""
    datos = filas_entrega(zona=zona, limite=limite, solo_contactables=solo_contactables)
    if not datos["items"]:
        return None
    extra = "solo las que tienen alguna vía de contacto" if solo_contactables else ""
    contenido = render_md(datos["items"], datos["total"], titulo_extra=extra)
    nombre = f"empresas_a_contactar_{date.today().isoformat()}_{datetime.now().strftime('%H%M%S')}.md"
    ruta = _carpeta_descargas() / nombre
    ruta.write_text(contenido, encoding="utf-8")
    return str(ruta)
