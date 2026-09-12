from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(tags=["trabajos"])


@router.get("/trabajos")
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [t.as_dict() for t in db.query(models.Trabajo).all()]
