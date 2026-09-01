"""Estado de ejecución persistente (para pausar/continuar entre reinicios)."""
from datetime import date

from app.db import get_conn, now


def get_state() -> dict:
    conn = get_conn()
    row = conn.execute("SELECT * FROM run_state WHERE id=1").fetchone()
    conn.close()
    return dict(row)


def set_status(status: str, zona_actual: str | None = None):
    conn = get_conn()
    if zona_actual is not None:
        conn.execute("UPDATE run_state SET status=?, zona_actual=?, actualizado_en=? WHERE id=1",
                     (status, zona_actual, now()))
    else:
        conn.execute("UPDATE run_state SET status=?, actualizado_en=? WHERE id=1", (status, now()))
    conn.commit()
    conn.close()


def registrar_queries(cantidad: int):
    conn = get_conn()
    hoy = date.today().isoformat()
    row = conn.execute("SELECT fecha_contador, queries_hoy FROM run_state WHERE id=1").fetchone()
    if row["fecha_contador"] != hoy:
        conn.execute("UPDATE run_state SET queries_hoy=?, fecha_contador=?, ultima_actividad=?, actualizado_en=? WHERE id=1",
                     (cantidad, hoy, now(), now()))
    else:
        conn.execute("UPDATE run_state SET queries_hoy=queries_hoy+?, ultima_actividad=?, actualizado_en=? WHERE id=1",
                     (cantidad, now(), now()))
    conn.commit()
    conn.close()


def queries_restantes_hoy(limite_diario: int) -> int:
    st = get_state()
    hoy = date.today().isoformat()
    usadas = st["queries_hoy"] if st["fecha_contador"] == hoy else 0
    return max(0, limite_diario - usadas)
