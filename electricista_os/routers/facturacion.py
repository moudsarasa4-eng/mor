"""Facturación. HOY es simulada (devuelve un CAE marcado como SIMULADO).

La integración fiscal real (ARCA vía TusFacturasAPP u otra) es el paso pendiente:
cuando exista, este endpoint devuelve el CAE real y el link al PDF. El dashboard
ya distingue el CAE "SIMULADO..." con una etiqueta, así que nada miente al usuario.
"""
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(tags=["facturacion"])


@router.post("/trabajos/{trabajo_id}/facturar")
def facturar(trabajo_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(models.Trabajo).filter_by(id=trabajo_id).first()
    if not t:
        raise HTTPException(404, "Trabajo no encontrado")
    cae = "SIMULADO" + str(random.randint(10000, 99999))
    t.cae = cae
    t.pdf_url = None
    db.commit()
    return {"cae": cae, "pdf_url": None, "simulado": True,
            "mensaje": "Facturación simulada — falta integrar ARCA/TusFacturasAPP para el CAE real."}
