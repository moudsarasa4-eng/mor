from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(tags=["insumos"])


@router.get("/insumos")
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [i.as_dict() for i in db.query(models.Insumo).all()]
