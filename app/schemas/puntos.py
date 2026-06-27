import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.puntos import EstadoCanje, TipoPunto


class RecompensaCreate(BaseModel):
    nombre: str
    descripcion: str | None = None
    costo_puntos: int
    stock: int = -1
    imagen_url: str | None = None


class RecompensaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    costo_puntos: int | None = None
    stock: int | None = None
    imagen_url: str | None = None
    activo: bool | None = None


class RecompensaOut(BaseModel):
    id: uuid.UUID
    nombre: str
    descripcion: str | None
    costo_puntos: int
    stock: int
    imagen_url: str | None
    activo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AsignarPuntosRequest(BaseModel):
    user_id: uuid.UUID
    cantidad: int
    motivo: str | None = None


class PuntosTransaccionOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    admin_id: uuid.UUID | None
    cantidad: int
    tipo: TipoPunto
    motivo: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CanjeCreate(BaseModel):
    recompensa_id: uuid.UUID


class CanjeOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    recompensa_id: uuid.UUID
    puntos_usados: int
    estado: EstadoCanje
    created_at: datetime
    procesado_at: datetime | None

    model_config = {"from_attributes": True}
