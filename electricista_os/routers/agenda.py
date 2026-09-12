import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..schemas import AgendaIn, EstadoIn
from .. import models

router = APIRouter(tags=["agenda"])

ESTADOS = {"PENDIENTE", "CONFIRMADA", "EN_CAMINO", "REALIZADA", "CANCELADA", "REPROGRAMADA"}


@router.get("/agenda")
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Visita).order_by(models.Visita.fecha_hora.asc()).all()
    return [v.as_dict() for v in q]


@router.patch("/agenda/{visita_id}/estado")
def cambiar_estado(visita_id: str, body: EstadoIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    v = db.query(models.Visita).filter_by(id=visita_id).first()
    if not v:
        raise HTTPException(404, "Visita no encontrada")
    if body.estado not in ESTADOS:
        raise HTTPException(422, f"Estado inválido. Válidos: {sorted(ESTADOS)}")
    v.estado = body.estado
    db.commit()
    return v.as_dict()


def _parse_fecha(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(422, "fecha_hora inválida (se espera ISO 8601)")


@router.post("/agenda")
def crear(body: AgendaIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    prospecto = db.query(models.Prospecto).filter_by(id=body.cliente_id).first()
    cliente = prospecto.nombre if prospecto else str(body.cliente_id)
    telefono = prospecto.telefono if prospecto else ""
    zona = body.zona or (prospecto.zona if prospecto else "")
    trabajo_tipo = ""
    if body.trabajo_id not in (None, ""):
        try:
            trabajo = db.query(models.Trabajo).filter_by(id=int(body.trabajo_id)).first()
            if trabajo:
                trabajo_tipo = trabajo.tipo
        except (ValueError, TypeError):
            pass
    v = models.Visita(
        id="v" + uuid.uuid4().hex[:8],
        cliente_id=body.cliente_id if prospecto else None,
        cliente=cliente, telefono=telefono,
        trabajo_id=int(body.trabajo_id) if str(body.trabajo_id).isdigit() else None,
        trabajo_tipo=trabajo_tipo,
        fecha_hora=_parse_fecha(body.fecha_hora),
        duracion_min=body.duracion_min or 60,
        zona=zona, estado="PENDIENTE", notas=body.notas or "",
    )
    db.add(v)
    db.commit()
    return v.as_dict()
