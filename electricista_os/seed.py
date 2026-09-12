"""Siembra datos iniciales (idempotente): usuario, empresa, insumos, prospectos,
trabajos y visitas de hoy — para que el dashboard muestre datos reales al entrar."""
import os
from datetime import datetime, timedelta

from .database import SessionLocal
from . import models
from .security import hash_password
from .diagnostico import procesar


def seed_all():
    db = SessionLocal()
    try:
        if not db.query(models.Usuario).first():
            user = os.environ.get("EOS_USER", "marco")
            pw = os.environ.get("EOS_PASSWORD", "electricista")
            db.add(models.Usuario(username=user, hashed_password=hash_password(pw)))

        if not db.query(models.Empresa).first():
            db.add(models.Empresa())

        if not db.query(models.Insumo).first():
            db.add_all([
                models.Insumo(nombre="Térmica Schneider 25A", proveedor="Casa Eléctrica Once", costo=8500, stock=2, stock_min=5),
                models.Insumo(nombre="Disyuntor diferencial 2x40A 30mA", proveedor="Electricidad Haedo", costo=46000, stock=3, stock_min=2),
                models.Insumo(nombre="Cable 2.5mm² (rollo)", proveedor="Cobla Electricidad", costo=1450, stock=120, stock_min=30),
                models.Insumo(nombre="Caja de embutir", proveedor="Cobla Electricidad", costo=1300, stock=40, stock_min=15),
            ])

        if not db.query(models.GastoOperativo).first():
            db.add_all([
                models.GastoOperativo(categoria="COMBUSTIBLE", monto=42000),
                models.GastoOperativo(categoria="HERRAMIENTAS", monto=18000),
            ])

        if not db.query(models.Prospecto).first():
            emp = db.query(models.Empresa).first()
            pv = emp.precio_visita_base if emp else 40000
            r1 = procesar("se me corta la luz y salta la térmica cuando prendo el aire, el tablero es viejo", pv)
            p1 = models.Prospecto(
                id="p1", nombre="Laura Giménez", telefono="11-3344-5566", zona="Hurlingham",
                estado="CALIFICADO", urgencia=r1["diagnostico"]["urgencia"],
                riesgo_tablero_detectado=True, presupuesto_estimado_rango="120000-250000",
                proximo_recordatorio=_hoy_str(), diagnostico=r1["diagnostico"],
                escenarios_presupuesto=r1["escenarios"],
                mensaje_original="se me corta la luz y salta la térmica cuando prendo el aire",
            )
            r2 = procesar("no anda un enchufe del living", pv)
            p2 = models.Prospecto(
                id="p2", nombre="Diego Martínez", telefono="11-5566-7788", zona="Morón",
                estado="VISITA_PROPUESTA", urgencia=r2["diagnostico"]["urgencia"],
                riesgo_tablero_detectado=False, presupuesto_estimado_rango="35000-60000",
                proximo_recordatorio=_hoy_str(), diagnostico=r2["diagnostico"],
                escenarios_presupuesto=r2["escenarios"],
                mensaje_original="no anda un enchufe del living",
            )
            db.add_all([p1, p2])

        if not db.query(models.Trabajo).first():
            t1 = models.Trabajo(cliente="Laura Giménez", cliente_id="p1",
                                tipo="Tablero seguro (Opción C)", monto_total=245000,
                                estado_pago="PENDIENTE", monto_cobrado=0)
            t1.insumos_usados = [
                models.InsumoUsado(nombre="Térmica Schneider 25A", cantidad=3, costo_unitario_historico=8500),
                models.InsumoUsado(nombre="Disyuntor diferencial 2x40A 30mA", cantidad=1, costo_unitario_historico=46000),
            ]
            t2 = models.Trabajo(cliente="Kiosco San Martín", tipo="Iluminación LED",
                                monto_total=98000, estado_pago="COBRADO", monto_cobrado=98000,
                                cae="70123456789012")
            t2.insumos_usados = [models.InsumoUsado(nombre="Cable 2.5mm² (rollo)", cantidad=1, costo_unitario_historico=1450)]
            db.add_all([t1, t2])

        if not db.query(models.Visita).first():
            now = datetime.now()
            db.add_all([
                models.Visita(id="v1", cliente_id="p1", cliente="Laura Giménez", telefono="11-3344-5566",
                              trabajo_tipo="Tablero seguro", fecha_hora=now + timedelta(hours=2),
                              duracion_min=60, zona="Hurlingham", estado="CONFIRMADA", notas="Revisión final"),
                models.Visita(id="v2", cliente_id="p2", cliente="Diego Martínez", telefono="11-5566-7788",
                              trabajo_tipo="Visita de diagnóstico", fecha_hora=now + timedelta(hours=4),
                              duracion_min=45, zona="Morón", estado="PENDIENTE", notas=""),
            ])

        db.commit()
    finally:
        db.close()


def _hoy_str():
    h = datetime.now()
    return f"{h.day:02d}/{h.month:02d}"
