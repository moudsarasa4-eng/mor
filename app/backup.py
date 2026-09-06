"""Backup automático de la base — si data/database.sqlite se corrompe o se
borra sin querer, antes se perdía todo el historial sin ningún respaldo.

Copia el archivo a data/backups/ con timestamp, y elimina los más viejos
para no acumular espacio indefinidamente (se queda con los últimos N).
"""
import shutil
from datetime import datetime

import app.db as db

MAX_BACKUPS = 30  # a 1 por hora en el modo automático, esto guarda ~30hs de historial


def _backups_dir():
    # calculado en cada llamada (no en el import) a partir de app.db.DB_PATH
    # actual: antes se fijaba una vez al importar el módulo, así que un test
    # que monkeypatchea db.DB_PATH para usar una base temporal terminaba
    # igual escribiendo/leyendo backups de la base REAL del usuario (pasó de
    # verdad: quedó un backup real huérfano en data/backups/ de una corrida
    # de tests anterior).
    return db.DB_PATH.parent / "backups"


def hacer_backup() -> str | None:
    if not db.DB_PATH.exists():
        return None
    backups_dir = _backups_dir()
    backups_dir.mkdir(parents=True, exist_ok=True)
    nombre = f"database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
    destino = backups_dir / nombre
    shutil.copy2(db.DB_PATH, destino)
    _limpiar_backups_viejos(backups_dir)
    return str(destino)


def _limpiar_backups_viejos(backups_dir):
    if not backups_dir.exists():
        return
    backups = sorted(backups_dir.glob("database_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    for viejo in backups[MAX_BACKUPS:]:
        viejo.unlink(missing_ok=True)


def restaurar_ultimo_backup() -> str | None:
    """Restaura el backup más reciente sobre database.sqlite. Uso manual,
    solo si la base actual está corrupta/perdida — pisa lo que haya."""
    backups_dir = _backups_dir()
    if not backups_dir.exists():
        return None
    backups = sorted(backups_dir.glob("database_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        return None
    shutil.copy2(backups[0], db.DB_PATH)
    return str(backups[0])
