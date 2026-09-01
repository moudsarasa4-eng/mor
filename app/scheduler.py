"""Modo automático: corre una tanda acotada de búsqueda cada N minutos (en vez
de quemar todo el presupuesto de una sola vez), respetando el presupuesto de
por vida (config.yaml discovery.lifetime_query_budget) para que dure semanas
en lugar de agotarse en una tarde."""
import threading
import time
from datetime import datetime, timedelta, timezone

from app import runner
from app.runner import CONFIG, presupuesto_lifetime_agotado
from app.run_state import set_status

_auto_enabled = threading.Event()
_auto_thread: threading.Thread | None = None
_thread_lock = threading.Lock()
_proxima_tanda: datetime | None = None


def proxima_tanda_en() -> str | None:
    if _proxima_tanda is None:
        return None
    return _proxima_tanda.isoformat()


def esta_activo() -> bool:
    return _auto_enabled.is_set()


def _loop_scheduler():
    global _proxima_tanda
    intervalo = CONFIG["discovery"]["scheduler"]["interval_minutes"] * 60
    batch = CONFIG["discovery"]["scheduler"]["batch_size"]

    while _auto_enabled.is_set():
        if presupuesto_lifetime_agotado():
            set_status("presupuesto_agotado")
            break

        runner.loop_investigacion(max_ciclos=batch)

        if not _auto_enabled.is_set():
            break

        _proxima_tanda = datetime.now(timezone.utc) + timedelta(seconds=intervalo)
        # dormir en pasos cortos para poder reaccionar rápido a un "detener"
        dormido = 0
        while dormido < intervalo and _auto_enabled.is_set():
            time.sleep(5)
            dormido += 5

    _proxima_tanda = None


def iniciar() -> bool:
    global _auto_thread
    with _thread_lock:
        if _auto_thread is not None and _auto_thread.is_alive():
            return False
        _auto_enabled.set()
        _auto_thread = threading.Thread(target=_loop_scheduler, daemon=True)
        _auto_thread.start()
        return True


def detener():
    global _proxima_tanda
    _auto_enabled.clear()
    _proxima_tanda = None
