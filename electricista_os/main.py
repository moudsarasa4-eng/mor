"""Electricista OS — app FastAPI.

Correr:  uvicorn electricista_os.main:app --reload
Abre el dashboard en http://127.0.0.1:8000  (login con el usuario sembrado).
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from . import models  # noqa: F401 (registra los modelos en Base)
from .seed import seed_all
from .routers import (auth, empresa, prospectos, trabajos, gastos, insumos,
                      agenda, diagnostico, facturacion)

app = FastAPI(title="Electricista OS API", version="1.0.0")

# CORS abierto: el dashboard puede abrirse como archivo (file://) o servido.
# No usamos cookies (auth por Bearer), así que allow_credentials=False + "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
seed_all()

for r in (auth, empresa, prospectos, trabajos, gastos, insumos, agenda, diagnostico, facturacion):
    app.include_router(r.router)


@app.get("/salud", tags=["salud"])
def salud():
    return {"ok": True, "servicio": "electricista-os"}


# Servir el dashboard estático en "/" (queda al final: las rutas de la API
# se resuelven primero). Así http://127.0.0.1:8000 abre la app directo.
_DASH = Path(__file__).resolve().parent.parent / "dashboard"
if _DASH.exists():
    app.mount("/", StaticFiles(directory=str(_DASH), html=True), name="dashboard")
