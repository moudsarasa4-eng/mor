from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..schemas import PromptIn
from ..diagnostico import escenarios_publicos, build_prompt

router = APIRouter(tags=["diagnostico"])


@router.get("/diagnostico/escenarios")
def escenarios(user=Depends(get_current_user)):
    return escenarios_publicos()


@router.post("/diagnostico/prompt")
def prompt(body: PromptIn, user=Depends(get_current_user)):
    return {"prompt": build_prompt(body.escenario_id, body.texto_cliente)}
