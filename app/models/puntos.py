import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TipoPunto(str, enum.Enum):
    asignacion_manual = "asignacion_manual"
    bono_reporte = "bono_reporte"
    bono_encontrado = "bono_encontrado"
    canje = "canje"


class EstadoCanje(str, enum.Enum):
    pendiente = "pendiente"
    entregado = "entregado"
    cancelado = "cancelado"


class PuntosTransaccion(Base):
    __tablename__ = "puntos_transacciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    admin_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    cantidad: Mapped[int] = mapped_column(Integer)
    tipo: Mapped[TipoPunto] = mapped_column(SAEnum(TipoPunto, name="tipo_punto"))
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    usuario: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="puntos_transacciones", foreign_keys=[user_id], lazy="raise"
    )
    admin: Mapped["User | None"] = relationship("User", foreign_keys=[admin_id], lazy="raise")  # noqa: F821


class Recompensa(Base):
    __tablename__ = "recompensas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    costo_puntos: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer, default=-1)
    imagen_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    canjes: Mapped[list["Canje"]] = relationship("Canje", back_populates="recompensa", lazy="raise")


class Canje(Base):
    __tablename__ = "canjes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    recompensa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recompensas.id"))
    puntos_usados: Mapped[int] = mapped_column(Integer)
    estado: Mapped[EstadoCanje] = mapped_column(SAEnum(EstadoCanje, name="estado_canje"), default=EstadoCanje.pendiente)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    procesado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    usuario: Mapped["User"] = relationship("User", back_populates="canjes", lazy="raise")  # noqa: F821
    recompensa: Mapped["Recompensa"] = relationship("Recompensa", back_populates="canjes", lazy="raise")
