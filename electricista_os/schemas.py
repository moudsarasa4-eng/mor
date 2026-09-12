"""Cuerpos de request (Pydantic). Las respuestas GET se arman con .as_dict()."""
from typing import Optional, Union
from pydantic import BaseModel


class ProcesarIn(BaseModel):
    texto: str


class PromptIn(BaseModel):
    escenario_id: str
    texto_cliente: str


class EstadoIn(BaseModel):
    estado: str


class AgendaIn(BaseModel):
    cliente_id: str
    trabajo_id: Optional[Union[str, int]] = None
    fecha_hora: str
    duracion_min: int = 60
    zona: Optional[str] = None
    notas: Optional[str] = None


class PagoIn(BaseModel):
    monto: float
    medio: Optional[str] = ""
    fecha: Optional[str] = None
    concepto: Optional[str] = ""


class MovimientoIn(BaseModel):
    tipo: str = "INGRESO"          # INGRESO | EGRESO
    monto: float
    medio: Optional[str] = ""
    concepto: Optional[str] = ""
    cliente: Optional[str] = ""
    fecha: Optional[str] = None


class ProspectoIn(BaseModel):
    nombre: str
    telefono: Optional[str] = ""
    zona: Optional[str] = ""
    estado: Optional[str] = "LEAD"
    urgencia: Optional[str] = None
    mensaje: Optional[str] = ""
