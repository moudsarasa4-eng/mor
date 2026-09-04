"""Promueve candidatas de discovered_companies_raw a la tabla companies.

Esto cierra el hueco del pipeline: sin este paso, discovery.py llenaba
discovered_companies_raw pero la tabla companies (y por lo tanto el dashboard,
"empresas verificadas" y "jackpots") quedaba vacía para siempre, sin importar
cuánto buscara el motor.

Importante: esto NO es "verificación" real ni scoring. Crea una empresa con
estado='candidata' (no aparece en el Top de oportunidades, que solo muestra
'jackpot'/'en_revision') a partir de heurísticas simples, para que quede
visible y lista para que un humano o una sesión de Claude Code la revise,
puntúe y audite con criterio real — igual que se hizo con Hurlingham.
"""
import re

from app.db import get_conn, now
from app.keywords import KEYWORDS_SEED
from app.exclusions import es_cadena_excluida

# keyword -> categoria, para inferir el rubro más probable de la candidata
_KEYWORD_A_CATEGORIA = {kw: cat for cat, kws in KEYWORDS_SEED.items() for kw in kws}


def _limpiar_nombre_final(nombre: str) -> str:
    nombre = re.sub(r"\s+", " ", nombre).strip()
    return nombre[:120]


def _inferir_rubro(keyword: str | None) -> str:
    if keyword and keyword in _KEYWORD_A_CATEGORIA:
        cat = _KEYWORD_A_CATEGORIA[keyword]
        if cat != "general":
            return cat
    return "logistica"  # default conservador; se corrige en la revisión real


def _tipo_fuente(url: str, nombre: str) -> str:
    """Heurística: si el dominio contiene una palabra del nombre, probablemente
    sea el sitio propio de la empresa; si no, es un directorio/agregador."""
    dom = re.sub(r"^https?://(www\.)?", "", url or "").split("/")[0].lower()
    palabras_nombre = [w.lower() for w in re.split(r"\W+", nombre) if len(w) > 3]
    if any(w in dom for w in palabras_nombre):
        return "sitio_propio"
    return "directorio"


def promover_candidatas(zona: str | None = None, limite: int = 100) -> dict:
    conn = get_conn()
    query = "SELECT d.*, q.keyword FROM discovered_companies_raw d " \
            "LEFT JOIN queries_log q ON q.id = d.query_id " \
            "WHERE d.company_id IS NULL"
    params = []
    if zona:
        query += " AND d.zona = ?"
        params.append(zona)
    query += " LIMIT ?"
    params.append(limite)

    filas = conn.execute(query, params).fetchall()
    promovidas = 0
    excluidas_cadena = 0
    for f in filas:
        nombre = _limpiar_nombre_final(f["nombre_crudo"])

        cadena = es_cadena_excluida(nombre)
        if cadena:
            conn.execute(
                "UPDATE discovered_companies_raw SET estado=? WHERE id=?",
                (f"EXCLUIDA_CADENA:{cadena}", f["id"]),
            )
            excluidas_cadena += 1
            continue

        rubro = _inferir_rubro(f["keyword"])

        existente = conn.execute("SELECT id FROM companies WHERE nombre = ?", (nombre,)).fetchone()
        if existente:
            company_id = existente["id"]
        else:
            ts = now()
            cur = conn.execute(
                "INSERT INTO companies (nombre, rubro, zona, localidad, actividad, estado, creado_en, actualizado_en) "
                "VALUES (?, ?, ?, ?, ?, 'candidata', ?, ?)",
                (nombre, rubro, f["zona"], f["zona"], (f["snippet"] or "")[:300], ts, ts),
            )
            company_id = cur.lastrowid

        if f["url"]:
            ya_tiene_fuente = conn.execute(
                "SELECT id FROM sources WHERE company_id=? AND url=?", (company_id, f["url"])
            ).fetchone()
            if not ya_tiene_fuente:
                conn.execute(
                    "INSERT INTO sources (company_id, url, tipo, descripcion, creado_en) VALUES (?, ?, ?, ?, ?)",
                    (company_id, f["url"], _tipo_fuente(f["url"], nombre), f["snippet"] or "", now()),
                )

        conn.execute(
            "UPDATE discovered_companies_raw SET company_id=?, estado='RELEVANT' WHERE id=?",
            (company_id, f["id"]),
        )
        promovidas += 1

    conn.commit()
    conn.close()
    return {"zona": zona, "candidatas_evaluadas": len(filas), "promovidas": promovidas,
            "excluidas_cadena": excluidas_cadena}
