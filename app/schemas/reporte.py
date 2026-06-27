import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.reporte import (
    DecisionValidacion,
    EstadoPublicacionReporte,
    EstadoResolucion,
    SubtipoAccidente,
    TipoReporte,
)


class ReporteCreate(BaseModel):
    tipo_reporte: TipoReporte
    subtipo_accidente: SubtipoAccidente | None = None
    titulo: str
    descripcion: str
    entidad_id: uuid.UUID | None = None
    nombre_desaparecido: str | None = None
    edad: int | None = None
    raza_especie: str | None = None
    color_descripcion: str | None = None
    ultima_ubicacion: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    fecha_desaparicion: datetime | None = None
    descripcion_vulnerabilidad: str | None = None


class ReporteUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    subtipo_accidente: SubtipoAccidente | None = None
    nombre_desaparecido: str | None = None
    edad: int | None = None
    raza_especie: str | None = None
    color_descripcion: str | None = None
    ultima_ubicacion: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    fecha_desaparicion: datetime | None = None
    descripcion_vulnerabilidad: str | None = None


class ReporteImagenOut(BaseModel):
    id: uuid.UUID
    reporte_id: uuid.UUID
    url: str
    orden: int

    model_config = {"from_attributes": True}


class ReporteOut(BaseModel):
    id: uuid.UUID
    creador_id: uuid.UUID
    entidad_id: uuid.UUID | None
    tipo_reporte: TipoReporte
    subtipo_accidente: SubtipoAccidente | None
    estado_publicacion: EstadoPublicacionReporte
    estado_resolucion: EstadoResolucion
    titulo: str
    descripcion: str
    nombre_desaparecido: str | None
    edad: int | None
    raza_especie: str | None
    color_descripcion: str | None
    ultima_ubicacion: str | None
    latitud: Decimal | None
    longitud: Decimal | None
    fecha_desaparicion: datetime | None
    descripcion_vulnerabilidad: str | None
    encontrado: bool
    found_at: datetime | None
    created_at: datetime
    updated_at: datetime
    imagenes: list[ReporteImagenOut] = []

    model_config = {"from_attributes": True}


class ReporteValidacionCreate(BaseModel):
    decision: DecisionValidacion
    motivo_rechazo: str | None = None


class ReporteValidacionOut(BaseModel):
    id: uuid.UUID
    reporte_id: uuid.UUID
    admin_id: uuid.UUID
    decision: DecisionValidacion
    motivo_rechazo: str | None
    validated_at: datetime

    model_config = {"from_attributes": True}


class MarcarEncontradoRequest(BaseModel):
    estado_resolucion: EstadoResolucion


class AgregarImagenRequest(BaseModel):
    url: str
    orden: int = 0
