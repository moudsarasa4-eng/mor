from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(tags=["empresa"])


@router.get("/empresa/configuracion")
def configuracion(db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = db.query(models.Empresa).first()
    return emp.as_dict() if emp else {"margen_insumos_default": 40, "precio_visita_base": 35000, "garantia_dias": 365}
