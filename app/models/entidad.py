import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TipoEntidad(str, enum.Enum):
    veterinaria = "veterinaria"
    hospital = "hospital"
    policia = "policia"
    otro = "otro"


class Entidad(Base):
    __tablename__ = "entidades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_creador_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    nombre: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[TipoEntidad] = mapped_column(SAEnum(TipoEntidad, name="tipo_entidad"))
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_contacto: Mapped[str | None] = mapped_column(String(150), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    admin_creador: Mapped["User"] = relationship("User", foreign_keys=[admin_creador_id], lazy="raise")  # noqa: F821
    usuarios: Mapped[list["EntidadUsuario"]] = relationship("EntidadUsuario", back_populates="entidad", lazy="raise")
    reportes: Mapped[list["Reporte"]] = relationship("Reporte", back_populates="entidad", lazy="raise")  # noqa: F821
    publicaciones: Mapped[list["Publicacion"]] = relationship("Publicacion", back_populates="entidad", lazy="raise")  # noqa: F821


class EntidadUsuario(Base):
    __tablename__ = "entidad_usuarios"
    __table_args__ = (UniqueConstraint("entidad_id", "user_id", name="uq_entidad_usuario"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entidades.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    asignado_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    entidad: Mapped["Entidad"] = relationship("Entidad", back_populates="usuarios", lazy="raise")
    usuario: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="entidades_asignadas", lazy="raise"
    )
