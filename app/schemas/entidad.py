import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.entidad import TipoEntidad


class EntidadCreate(BaseModel):
    nombre: str
    tipo: TipoEntidad
    direccion: str | None = None
    email_contacto: str | None = None
    logo_url: str | None = None
    telefono: str | None = None


class EntidadUpdate(BaseModel):
    nombre: str | None = None
    tipo: TipoEntidad | None = None
    direccion: str | None = None
    email_contacto: str | None = None
    logo_url: str | None = None
    telefono: str | None = None
    activo: bool | None = None


class EntidadOut(BaseModel):
    id: uuid.UUID
    admin_creador_id: uuid.UUID
    nombre: str
    tipo: TipoEntidad
    direccion: str | None
    email_contacto: str | None
    logo_url: str | None
    telefono: str | None
    activo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AsignarUsuarioRequest(BaseModel):
    user_id: uuid.UUID


class EntidadUsuarioOut(BaseModel):
    id: uuid.UUID
    entidad_id: uuid.UUID
    user_id: uuid.UUID
    asignado_at: datetime

    model_config = {"from_attributes": True}
