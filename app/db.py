"""Acceso a la base SQLite (data/database.sqlite) — "el cerebro estructurado"."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database.sqlite"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_conn()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    _seed_keywords(conn)
    conn.commit()
    conn.close()


def _seed_keywords(conn):
    from app.keywords import KEYWORDS_SEED
    for categoria, terminos in KEYWORDS_SEED.items():
        for termino in terminos:
            conn.execute(
                "INSERT OR IGNORE INTO keywords (termino, categoria, origen, creado_en) VALUES (?, ?, 'seed', ?)",
                (termino, categoria, now()),
            )


if __name__ == "__main__":
    init_db()
    print(f"Base inicializada en {DB_PATH}")
