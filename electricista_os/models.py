"""Modelos SQLAlchemy. La forma serializada respeta el contrato del dashboard."""
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, Boolean, DateTime,
                        ForeignKey, JSON, Text)
from sqlalchemy.orm import relationship
from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(Integer, primary_key=True)
    margen_insumos_default = Column(Float, default=40)
    precio_visita_base = Column(Float, default=35000)
    garantia_dias = Column(Integer, default=365)
    negocio = Column(String, default="Electricista OS")
    titular = Column(String, default="Marco")
    meta_mensual = Column(Float, default=1500000)

    def as_dict(self):
        return {
            "margen_insumos_default": self.margen_insumos_default,
            "precio_visita_base": self.precio_visita_base,
            "garantia_dias": self.garantia_dias,
            "negocio": self.negocio,
            "titular": self.titular,
            "meta_mensual": self.meta_mensual,
        }


class Prospecto(Base):
    __tablename__ = "prospectos"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, default="")
    zona = Column(String, default="")
    direccion = Column(String, default="")
    estado = Column(String, default="LEAD")
    urgencia = Column(String, nullable=True)
    riesgo_tablero_detectado = Column(Boolean, default=False)
    presupuesto_estimado_rango = Column(String, default="")
    proximo_recordatorio = Column(String, default="")
    diagnostico = Column(JSON, nullable=True)
    escenarios_presupuesto = Column(JSON, nullable=True)
    mensaje_original = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "zona": self.zona,
            "direccion": self.direccion,
            "estado": self.estado,
            "urgencia": self.urgencia,
            "riesgo_tablero_detectado": self.riesgo_tablero_detectado,
            "presupuesto_estimado_rango": self.presupuesto_estimado_rango,
            "proximo_recordatorio": self.proximo_recordatorio,
            "diagnostico": self.diagnostico,
            "escenarios_presupuesto": self.escenarios_presupuesto or [],
        }


class Insumo(Base):
    __tablename__ = "insumos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    proveedor = Column(String, default="")
    costo = Column(Float, default=0)
    stock = Column(Integer, default=0)
    stock_min = Column(Integer, default=0)

    def as_dict(self):
        return {"id": self.id, "nombre": self.nombre, "proveedor": self.proveedor,
                "costo": self.costo, "stock": self.stock, "stock_min": self.stock_min}


class Trabajo(Base):
    __tablename__ = "trabajos"
    id = Column(Integer, primary_key=True)
    cliente = Column(String, default="")
    cliente_id = Column(String, ForeignKey("prospectos.id"), nullable=True)
    tipo = Column(String, default="")
    monto_total = Column(Float, default=0)
    estado_pago = Column(String, default="PENDIENTE")
    monto_cobrado = Column(Float, default=0)
    cae = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    insumos_usados = relationship("InsumoUsado", back_populates="trabajo",
                                  cascade="all, delete-orphan")

    def as_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente,
            "cliente_id": self.cliente_id,
            "tipo": self.tipo,
            "monto_total": self.monto_total,
            "estado_pago": self.estado_pago,
            "monto_cobrado": self.monto_cobrado,
            "cae": self.cae,
            "pdf_url": self.pdf_url,
            # El dashboard mapea insumos_usados -> {insumo:{nombre}, cantidad, costo_unitario_historico}
            "insumos_usados": [iu.as_dict() for iu in self.insumos_usados],
        }


class InsumoUsado(Base):
    __tablename__ = "insumos_usados"
    id = Column(Integer, primary_key=True)
    trabajo_id = Column(Integer, ForeignKey("trabajos.id"))
    insumo_id = Column(Integer, ForeignKey("insumos.id"), nullable=True)
    nombre = Column(String, default="")
    cantidad = Column(Float, default=1)
    costo_unitario_historico = Column(Float, default=0)
    trabajo = relationship("Trabajo", back_populates="insumos_usados")
    insumo = relationship("Insumo")

    def as_dict(self):
        nombre = self.nombre or (self.insumo.nombre if self.insumo else "")
        return {
            "insumo": {"nombre": nombre},
            "nombre": nombre,
            "cantidad": self.cantidad,
            "costo_unitario_historico": self.costo_unitario_historico,
        }


class GastoOperativo(Base):
    __tablename__ = "gastos"
    id = Column(Integer, primary_key=True)
    categoria = Column(String, default="")
    monto = Column(Float, default=0)
    fecha = Column(DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {"id": self.id, "categoria": self.categoria, "monto": self.monto,
                "fecha": self.fecha.isoformat() if self.fecha else None}


class Visita(Base):
    __tablename__ = "visitas"
    id = Column(String, primary_key=True)
    cliente_id = Column(String, ForeignKey("prospectos.id"), nullable=True)
    cliente = Column(String, default="")
    telefono = Column(String, default="")
    trabajo_id = Column(Integer, ForeignKey("trabajos.id"), nullable=True)
    trabajo_tipo = Column(String, default="")
    fecha_hora = Column(DateTime, nullable=False)
    duracion_min = Column(Integer, default=60)
    zona = Column(String, default="")
    estado = Column(String, default="PENDIENTE")
    notas = Column(String, default="")
    link_maps = Column(String, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente,
            "telefono": self.telefono,
            "trabajo_tipo": self.trabajo_tipo,
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "duracion_min": self.duracion_min,
            "zona": self.zona,
            "estado": self.estado,
            "notas": self.notas,
            "link_maps": self.link_maps,
        }
