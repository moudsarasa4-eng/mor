import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..schemas import ProcesarIn, ProspectoIn
from ..diagnostico import procesar
from .. import models

router = APIRouter(tags=["prospectos"])


@router.get("/prospectos")
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [p.as_dict() for p in db.query(models.Prospecto).order_by(models.Prospecto.created_at.desc()).all()]


@router.post("/prospectos/procesar")
def procesar_texto(body: ProcesarIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = db.query(models.Empresa).first()
    pv = emp.precio_visita_base if emp else 40000
    res = procesar(body.texto, pv)
    pid = uuid.uuid4().hex
    p = models.Prospecto(
        id=pid,
        nombre="Consulta sin nombre",
        estado="LEAD",
        urgencia=res["diagnostico"]["urgencia"],
        riesgo_tablero_detectado=res["riesgo_tablero"],
        presupuesto_estimado_rango=res["rango"],
        diagnostico=res["diagnostico"],
        escenarios_presupuesto=res["escenarios"],
        mensaje_original=body.texto,
    )
    db.add(p)
    db.commit()
    return {"prospecto_id": pid, "diagnostico": res["diagnostico"], "escenarios": res["escenarios"]}


@router.post("/prospectos")
def crear(body: ProspectoIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Alta manual (ej: desde el intake de WhatsApp con nombre y teléfono)."""
    emp = db.query(models.Empresa).first()
    pv = emp.precio_visita_base if emp else 40000
    res = procesar(body.mensaje or "", pv) if body.mensaje else None
    pid = uuid.uuid4().hex
    p = models.Prospecto(
        id=pid,
        nombre=body.nombre or "Cliente WhatsApp",
        telefono=body.telefono or "",
        zona=body.zona or "",
        estado=body.estado or "LEAD",
        urgencia=body.urgencia or (res["diagnostico"]["urgencia"] if res else None),
        riesgo_tablero_detectado=res["riesgo_tablero"] if res else False,
        presupuesto_estimado_rango=res["rango"] if res else "",
        diagnostico=res["diagnostico"] if res else None,
        escenarios_presupuesto=res["escenarios"] if res else [],
        mensaje_original=body.mensaje or "",
    )
    db.add(p)
    db.commit()
    return p.as_dict()
