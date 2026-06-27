import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TipoPublicacion(str, enum.Enum):
    evento = "evento"
    campana = "campana"
    adopcion = "adopcion"
    voluntariado = "voluntariado"


class EstadoPublicacionPub(str, enum.Enum):
    borrador = "borrador"
    publicado = "publicado"
    archivado = "archivado"


class Publicacion(Base):
    __tablename__ = "publicaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    autor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    entidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entidades.id"))
    tipo_publicacion: Mapped[TipoPublicacion] = mapped_column(SAEnum(TipoPublicacion, name="tipo_publicacion"))
    estado: Mapped[EstadoPublicacionPub] = mapped_column(
        SAEnum(EstadoPublicacionPub, name="estado_publicacion_pub"), default=EstadoPublicacionPub.borrador
    )
    titulo: Mapped[str] = mapped_column(String(200))
    contenido: Mapped[str] = mapped_column(Text)
    fecha_evento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lugar_evento: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cupos_disponibles: Mapped[int | None] = mapped_column(Integer, nullable=True)
    especie_mascota: Mapped[str | None] = mapped_column(String(80), nullable=True)
    raza_mascota: Mapped[str | None] = mapped_column(String(80), nullable=True)
    edad_mascota: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sexo_mascota: Mapped[str | None] = mapped_column(String(10), nullable=True)
    castrado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    autor: Mapped["User"] = relationship("User", foreign_keys=[autor_id], lazy="raise")  # noqa: F821
    entidad: Mapped["Entidad"] = relationship("Entidad", back_populates="publicaciones", lazy="raise")  # noqa: F821
    imagenes: Mapped[list["PublicacionImagen"]] = relationship(
        "PublicacionImagen", back_populates="publicacion", cascade="all, delete-orphan", lazy="raise"
    )


class PublicacionImagen(Base):
    __tablename__ = "publicacion_imagenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publicacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publicaciones.id", ondelete="CASCADE")
    )
    url: Mapped[str] = mapped_column(Text)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    publicacion: Mapped["Publicacion"] = relationship("Publicacion", back_populates="imagenes", lazy="raise")
