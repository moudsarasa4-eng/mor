"""Caza de proveedores/fabricantes industriales por rubro CLAE, cruzado con
partidos del oeste del GBA. Reusa el mismo pipeline de búsqueda/dedupe/
promoción que discovery.py — no genera un formato de salida aparte: las
candidatas terminan en la misma tabla companies, con el mismo export a .txt.

Fuentes usadas: Serper (búsqueda web general) + cuitonline (vía query
dirigida). Deliberadamente NO incluye:
- Google Maps API (requeriría otra API key con costo, no configurada).
- Scraping de avisos vencidos en ZonaJobs/Bumeran (viola sus términos de uso).
"""
import re

from app.db import get_conn, now
from app.discovery import ejecutar_query
from app.promote import promover_candidatas
from app.rubros_industriales import RUBROS_CLAE, PARTIDOS_DEFAULT


def _queries_por_rubro(rubro_nombre: str, partido: str) -> list[dict]:
    return [
        {"query": f'"{rubro_nombre}" {partido} empresa', "tipo": "TYPE_C", "keyword": rubro_nombre},
        {"query": f'{rubro_nombre} {partido} site:cuitonline.com', "tipo": "TYPE_C", "keyword": rubro_nombre},
        {"query": f'"{rubro_nombre}" "{partido}" fábrica OR planta OR industria', "tipo": "TYPE_C", "keyword": rubro_nombre},
    ]


def pendientes(partidos: list[str] | None = None) -> list[tuple[str, str, str]]:
    """Devuelve (partido, codigo, nombre) de combinaciones todavía no procesadas."""
    partidos = partidos or PARTIDOS_DEFAULT
    conn = get_conn()
    procesados = {
        (r["partido"], r["codigo_claé"])
        for r in conn.execute("SELECT partido, codigo_claé FROM industrial_progress")
    }
    conn.close()
    out = []
    for partido in partidos:
        for codigo, nombre in RUBROS_CLAE.items():
            if (partido, codigo) not in procesados:
                out.append((partido, codigo, nombre))
    return out


def procesar_rubro(partido: str, codigo: str, rubro_nombre: str) -> dict:
    queries = _queries_por_rubro(rubro_nombre, partido)
    nuevas_totales = 0
    for q in queries:
        r = ejecutar_query(q["query"], partido, q["tipo"], q["keyword"])
        nuevas_totales += r.get("empresas_nuevas", 0)

    promover_candidatas(zona=partido)

    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO industrial_progress (partido, codigo_claé, rubro_nombre, empresas_nuevas, procesado_en) "
        "VALUES (?, ?, ?, ?, ?)",
        (partido, codigo, rubro_nombre, nuevas_totales, now()),
    )
    conn.commit()
    conn.close()
    return {"partido": partido, "codigo": codigo, "rubro": rubro_nombre, "empresas_nuevas": nuevas_totales}


def correr_lote(partidos: list[str] | None = None, max_rubros: int = 10) -> dict:
    """Procesa hasta max_rubros combinaciones (partido, rubro) pendientes.
    Resumible: cada combinación ya procesada se salta en la próxima corrida."""
    tareas = pendientes(partidos)[:max_rubros]
    resultados = [procesar_rubro(*t) for t in tareas]
    return {
        "procesados": len(resultados),
        "pendientes_restantes": len(pendientes(partidos)) - len(resultados),
        "empresas_nuevas_totales": sum(r["empresas_nuevas"] for r in resultados),
        "detalle": resultados,
    }
