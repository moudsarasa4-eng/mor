from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(tags=["gastos"])


@router.get("/gastos-operativos")
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [g.as_dict() for g in db.query(models.GastoOperativo).all()]
