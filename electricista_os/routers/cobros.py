"""Cobros y caja: registrar pagos (con antigüedad de deuda) y movimientos de caja."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..schemas import PagoIn, MovimientoIn
from .. import models

router = APIRouter(tags=["cobros"])


def _fecha(s):
    if not s:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return datetime.utcnow()


@router.post("/trabajos/{trabajo_id}/pago")
def registrar_pago(trabajo_id: int, body: PagoIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(models.Trabajo).filter_by(id=trabajo_id).first()
    if not t:
        raise HTTPException(404, "Trabajo no encontrado")
    if body.monto <= 0:
        raise HTTPException(422, "El monto del pago debe ser mayor a 0")
    t.monto_cobrado = (t.monto_cobrado or 0) + body.monto
    if t.monto_cobrado >= (t.monto_total or 0):
        t.estado_pago = "COBRADO"
        t.monto_cobrado = t.monto_total  # no pasar del total
    elif t.monto_cobrado > 0:
        t.estado_pago = "PARCIAL"
    mov = models.Movimiento(
        tipo="INGRESO", monto=body.monto, medio=body.medio or "",
        concepto=body.concepto or ("Cobro: " + (t.tipo or "trabajo")),
        cliente=t.cliente or "", trabajo_id=t.id, fecha=_fecha(body.fecha),
    )
    db.add(mov)
    db.commit()
    return {"trabajo": t.as_dict(), "movimiento": mov.as_dict()}


@router.get("/caja/movimientos")
def listar_movimientos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Movimiento).order_by(models.Movimiento.fecha.desc()).all()
    return [m.as_dict() for m in q]


@router.post("/caja/movimiento")
def crear_movimiento(body: MovimientoIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if body.monto <= 0:
        raise HTTPException(422, "El monto debe ser mayor a 0")
    tipo = "EGRESO" if str(body.tipo).upper() == "EGRESO" else "INGRESO"
    mov = models.Movimiento(
        tipo=tipo, monto=body.monto, medio=body.medio or "",
        concepto=body.concepto or "", cliente=body.cliente or "", fecha=_fecha(body.fecha),
    )
    db.add(mov)
    db.commit()
    return mov.as_dict()
