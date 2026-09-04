"""Backup automático de la base — si data/database.sqlite se corrompe o se
borra sin querer, antes se perdía todo el historial sin ningún respaldo.

Copia el archivo a data/backups/ con timestamp, y elimina los más viejos
para no acumular espacio indefinidamente (se queda con los últimos N).
"""
import shutil
from datetime import datetime
from pathlib import Path

from app.db import DB_PATH

BACKUPS_DIR = DB_PATH.parent / "backups"
MAX_BACKUPS = 30  # a 1 por hora en el modo automático, esto guarda ~30hs de historial


def hacer_backup() -> str | None:
    if not DB_PATH.exists():
        return None
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    nombre = f"database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
    destino = BACKUPS_DIR / nombre
    shutil.copy2(DB_PATH, destino)
    _limpiar_backups_viejos()
    return str(destino)


def _limpiar_backups_viejos():
    if not BACKUPS_DIR.exists():
        return
    backups = sorted(BACKUPS_DIR.glob("database_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    for viejo in backups[MAX_BACKUPS:]:
        viejo.unlink(missing_ok=True)


def restaurar_ultimo_backup() -> str | None:
    """Restaura el backup más reciente sobre database.sqlite. Uso manual,
    solo si la base actual está corrupta/perdida — pisa lo que haya."""
    if not BACKUPS_DIR.exists():
        return None
    backups = sorted(BACKUPS_DIR.glob("database_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        return None
    shutil.copy2(backups[0], DB_PATH)
    return str(backups[0])
