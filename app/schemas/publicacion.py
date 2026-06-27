import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.publicacion import EstadoPublicacionPub, TipoPublicacion


class PublicacionCreate(BaseModel):
    entidad_id: uuid.UUID
    tipo_publicacion: TipoPublicacion
    titulo: str
    contenido: str
    fecha_evento: datetime | None = None
    lugar_evento: str | None = None
    cupos_disponibles: int | None = None
    especie_mascota: str | None = None
    raza_mascota: str | None = None
    edad_mascota: int | None = None
    sexo_mascota: str | None = None
    castrado: bool | None = None


class PublicacionUpdate(BaseModel):
    titulo: str | None = None
    contenido: str | None = None
    fecha_evento: datetime | None = None
    lugar_evento: str | None = None
    cupos_disponibles: int | None = None
    especie_mascota: str | None = None
    raza_mascota: str | None = None
    edad_mascota: int | None = None
    sexo_mascota: str | None = None
    castrado: bool | None = None


class PublicacionImagenOut(BaseModel):
    id: uuid.UUID
    publicacion_id: uuid.UUID
    url: str
    orden: int

    model_config = {"from_attributes": True}


class PublicacionOut(BaseModel):
    id: uuid.UUID
    autor_id: uuid.UUID
    entidad_id: uuid.UUID
    tipo_publicacion: TipoPublicacion
    estado: EstadoPublicacionPub
    titulo: str
    contenido: str
    fecha_evento: datetime | None
    lugar_evento: str | None
    cupos_disponibles: int | None
    especie_mascota: str | None
    raza_mascota: str | None
    edad_mascota: int | None
    sexo_mascota: str | None
    castrado: bool | None
    created_at: datetime
    updated_at: datetime
    imagenes: list[PublicacionImagenOut] = []

    model_config = {"from_attributes": True}


class CambiarEstadoRequest(BaseModel):
    estado: EstadoPublicacionPub


class AgregarImagenRequest(BaseModel):
    url: str
    orden: int = 0
