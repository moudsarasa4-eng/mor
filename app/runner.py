"""Orquestador de la investigación continua: elige zona, corre discovery con
presupuesto, guarda estado, permite pausar entre queries."""
import threading
import time
from pathlib import Path

import yaml

from app.db import get_conn, now
from app.discovery import ejecutar_query
from app.keywords import KEYWORDS_SEED, plantillas_query
from app.promote import promover_candidatas
from app.export_txt import exportar_candidatas_txt
from app.backup import hacer_backup
from app.run_state import get_state, set_status, registrar_queries, queries_restantes_hoy

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = yaml.safe_load((BASE_DIR / "config.yaml").read_text(encoding="utf-8"))

_pause_event = threading.Event()  # set = correr, clear = pausado
_pause_event.set()
_stop_event = threading.Event()


def orden_zonas() -> list[str]:
    return CONFIG["zonas"]["cercana"] + CONFIG["zonas"]["media"] + CONFIG["zonas"]["extendida"]


def queries_lifetime_usadas() -> int:
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) c FROM queries_log").fetchone()["c"]
    conn.close()
    return n


def presupuesto_lifetime_agotado() -> bool:
    return queries_lifetime_usadas() >= CONFIG["discovery"]["lifetime_query_budget"]


def zona_saturada(zona: str) -> bool:
    conn = get_conn()
    rows = conn.execute(
        "SELECT empresas_nuevas FROM queries_log WHERE zona=? ORDER BY id DESC LIMIT ?",
        (zona, CONFIG["discovery"]["saturation_rounds"]),
    ).fetchall()
    conn.close()
    if len(rows) < CONFIG["discovery"]["saturation_rounds"]:
        return False
    return all(r["empresas_nuevas"] == 0 for r in rows)


def siguiente_zona_no_saturada() -> str | None:
    for z in orden_zonas():
        if not zona_saturada(z):
            return z
    return None


def pausar():
    _pause_event.clear()
    set_status("paused")


def continuar():
    _pause_event.set()
    set_status("running")


def detener():
    _stop_event.set()
    _pause_event.set()  # despertar si estaba pausado, para que salga del loop


def _keywords_por_prioridad() -> list[str]:
    """Ordena las keywords por rendimiento aprendido (yield_score), para que un
    presupuesto acotado se gaste primero en lo que ya demostró funcionar.
    Las que todavía no se probaron (queries_usadas=0) van primero que las de
    yield bajo confirmado, para no dejar de explorar nunca."""
    conn = get_conn()
    filas = {r["termino"]: (r["queries_usadas"], r["yield_score"]) for r in conn.execute(
        "SELECT termino, queries_usadas, yield_score FROM keywords"
    )}
    conn.close()
    todas_keywords = [kw for lista in KEYWORDS_SEED.values() for kw in lista]

    def score(kw: str) -> tuple:
        usadas, yield_score = filas.get(kw, (0, 0.0))
        si_no_probada = 0 if usadas == 0 else 1  # 0 = probarla ya, 1 = ya se probó
        return (si_no_probada, -yield_score)

    return sorted(todas_keywords, key=score)


def _generar_lote_queries(zona: str) -> list[dict]:
    queries = []
    for kw in _keywords_por_prioridad():
        queries.extend(plantillas_query(zona, kw))
    queries.extend(plantillas_query(zona))
    return queries


def loop_investigacion(max_ciclos: int | None = None, max_minutos: float | None = None):
    """Bucle principal: recorre zonas no saturadas ejecutando queries de a una,
    respetando pausa, límite diario y presupuesto por zona. Pensado para correr
    en un thread de background desde la web app.

    max_minutos acota por TIEMPO (ej. tanda de 2 horas) en vez de por cantidad
    fija de queries — el motor sigue buscando mientras haya tiempo, presupuesto
    y zonas no saturadas."""
    _stop_event.clear()
    set_status("running")
    ciclos = 0
    inicio = time.monotonic()
    limite_diario = CONFIG["discovery"]["daily"]["max_queries"]

    def tiempo_agotado() -> bool:
        return max_minutos is not None and (time.monotonic() - inicio) >= max_minutos * 60

    while not _stop_event.is_set():
        if max_ciclos is not None and ciclos >= max_ciclos:
            break
        if tiempo_agotado():
            break

        _pause_event.wait()  # bloquea acá si está pausado
        if _stop_event.is_set():
            break

        if presupuesto_lifetime_agotado():
            set_status("presupuesto_agotado")
            break

        zona = siguiente_zona_no_saturada()
        if zona is None:
            set_status("idle")
            break

        set_status("running", zona_actual=zona)
        restantes_hoy = queries_restantes_hoy(limite_diario)
        if restantes_hoy <= 0:
            set_status("idle")
            break

        queries = _generar_lote_queries(zona)
        max_zona = min(CONFIG["discovery"]["max_queries_per_zone"], restantes_hoy)

        racha_sin_nuevas = 0
        for q in queries[:max_zona]:
            _pause_event.wait()
            if _stop_event.is_set() or presupuesto_lifetime_agotado() or tiempo_agotado():
                break
            r = ejecutar_query(q["query"], zona, q["tipo"], q.get("keyword", ""))
            registrar_queries(1)
            ciclos += 1
            time.sleep(0.4)  # cortesía con la API de búsqueda, evita 429 innecesarios
            if r.get("empresas_nuevas", 0) == 0:
                racha_sin_nuevas += 1
            else:
                racha_sin_nuevas = 0
            if racha_sin_nuevas >= CONFIG["discovery"]["saturation_rounds"]:
                break
            if max_ciclos is not None and ciclos >= max_ciclos:
                break

        promover_candidatas(zona=zona)

        # todas las fuentes en el mismo ciclo, para que un solo botón cubra todo:
        # búsqueda geográfica (arriba) + industrial CLAE + proveedores de góndola
        # + contacto — pero TODAS descuentan del mismo presupuesto max_ciclos,
        # sino una corrida "de 8" podría terminar gastando 25-30 búsquedas reales.
        def _presupuesto_agotado_para_esta_corrida() -> bool:
            return max_ciclos is not None and ciclos >= max_ciclos

        def _gastar(fn, *args, **kwargs):
            nonlocal ciclos
            antes = queries_lifetime_usadas()
            resultado = fn(*args, **kwargs)
            ciclos += queries_lifetime_usadas() - antes
            return resultado

        if not tiempo_agotado() and not presupuesto_lifetime_agotado() and not _presupuesto_agotado_para_esta_corrida():
            from app.industrial_discovery import correr_lote as correr_industrial
            _gastar(correr_industrial, max_rubros=1)
        if not tiempo_agotado() and not presupuesto_lifetime_agotado() and not _presupuesto_agotado_para_esta_corrida():
            from app.supplier_discovery import correr_lote as correr_supplier
            _gastar(correr_supplier, zona=zona, max_categorias=1)
        if not tiempo_agotado() and not presupuesto_lifetime_agotado() and not _presupuesto_agotado_para_esta_corrida():
            from app.contact_finder import correr_lote as correr_contactos
            _gastar(correr_contactos, zona=zona, limite=3)

        archivo_txt = exportar_candidatas_txt()  # sin filtro de zona: incluye lo que sumaron industrial/supplier
        if archivo_txt:
            print(f"[Motor de Jackpots] Candidatas exportadas a: {archivo_txt}")

    hacer_backup()

    if get_state()["status"] not in ("presupuesto_agotado",):
        set_status("idle")


_thread: threading.Thread | None = None
_thread_lock = threading.Lock()


def iniciar_en_background(max_ciclos: int | None = None, max_minutos: float | None = None):
    global _thread
    with _thread_lock:
        if _thread is not None and _thread.is_alive():
            return False  # ya corriendo, evita hilos duplicados por doble-click
        _pause_event.set()
        _thread = threading.Thread(
            target=loop_investigacion,
            kwargs={"max_ciclos": max_ciclos, "max_minutos": max_minutos},
            daemon=True,
        )
        _thread.start()
        return True
