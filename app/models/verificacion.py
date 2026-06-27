import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class EstadoVerificacion(str, enum.Enum):
    pendiente = "pendiente"
    verificado = "verificado"
    rechazado = "rechazado"


class VerificacionIdentidad(Base):
    __tablename__ = "verificaciones_identidad"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    url_anverso: Mapped[str] = mapped_column(Text)
    url_reverso: Mapped[str] = mapped_column(Text)
    estado: Mapped[EstadoVerificacion] = mapped_column(
        SAEnum(EstadoVerificacion, name="estado_verificacion"), default=EstadoVerificacion.pendiente
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    usuario: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="verificaciones", foreign_keys=[user_id], lazy="raise"
    )
    admin: Mapped["User | None"] = relationship("User", foreign_keys=[admin_id], lazy="raise")  # noqa: F821
