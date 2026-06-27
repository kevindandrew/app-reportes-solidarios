import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class RolUsuario(str, enum.Enum):
    administrador = "administrador"
    entidad = "entidad"
    usuario = "usuario"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(80))
    apellido: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    rol: Mapped[RolUsuario] = mapped_column(SAEnum(RolUsuario, name="rol_usuario"), default=RolUsuario.usuario)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    puntos_totales: Mapped[int] = mapped_column(Integer, default=0)
    foto_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reportes: Mapped[list["Reporte"]] = relationship(  # noqa: F821
        "Reporte", back_populates="creador", foreign_keys="[Reporte.creador_id]", lazy="raise"
    )
    entidades_asignadas: Mapped[list["EntidadUsuario"]] = relationship(  # noqa: F821
        "EntidadUsuario", back_populates="usuario", lazy="raise"
    )
    puntos_transacciones: Mapped[list["PuntosTransaccion"]] = relationship(  # noqa: F821
        "PuntosTransaccion", back_populates="usuario", foreign_keys="[PuntosTransaccion.user_id]", lazy="raise"
    )
    canjes: Mapped[list["Canje"]] = relationship("Canje", back_populates="usuario", lazy="raise")  # noqa: F821
    verificaciones: Mapped[list["VerificacionIdentidad"]] = relationship(  # noqa: F821
        "VerificacionIdentidad", back_populates="usuario", foreign_keys="[VerificacionIdentidad.user_id]", lazy="raise"
    )
