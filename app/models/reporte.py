import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TipoReporte(str, enum.Enum):
    persona_desaparecida = "persona_desaparecida"
    animal_desaparecido = "animal_desaparecido"
    accidente = "accidente"
    vulnerabilidad = "vulnerabilidad"


class SubtipoAccidente(str, enum.Enum):
    atropello = "atropello"
    desastre_natural = "desastre_natural"
    incendio = "incendio"
    otro = "otro"


class EstadoPublicacionReporte(str, enum.Enum):
    pendiente = "pendiente"
    aceptado = "aceptado"
    rechazado = "rechazado"


class EstadoResolucion(str, enum.Enum):
    activo = "activo"
    encontrado = "encontrado"
    atendido = "atendido"
    cerrado = "cerrado"


class DecisionValidacion(str, enum.Enum):
    aceptado = "aceptado"
    rechazado = "rechazado"


class Reporte(Base):
    __tablename__ = "reportes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creador_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    entidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("entidades.id"), nullable=True)
    tipo_reporte: Mapped[TipoReporte] = mapped_column(SAEnum(TipoReporte, name="tipo_reporte"))
    subtipo_accidente: Mapped[SubtipoAccidente | None] = mapped_column(
        SAEnum(SubtipoAccidente, name="subtipo_accidente"), nullable=True
    )
    estado_publicacion: Mapped[EstadoPublicacionReporte] = mapped_column(
        SAEnum(EstadoPublicacionReporte, name="estado_publicacion_reporte"),
        default=EstadoPublicacionReporte.pendiente,
    )
    estado_resolucion: Mapped[EstadoResolucion] = mapped_column(
        SAEnum(EstadoResolucion, name="estado_resolucion"), default=EstadoResolucion.activo
    )
    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text)
    nombre_desaparecido: Mapped[str | None] = mapped_column(String(120), nullable=True)
    edad: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raza_especie: Mapped[str | None] = mapped_column(String(80), nullable=True)
    color_descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ultima_ubicacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    fecha_desaparicion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    descripcion_vulnerabilidad: Mapped[str | None] = mapped_column(Text, nullable=True)
    encontrado: Mapped[bool] = mapped_column(Boolean, default=False)
    found_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creador: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="reportes", foreign_keys=[creador_id], lazy="raise"
    )
    entidad: Mapped["Entidad"] = relationship("Entidad", back_populates="reportes", lazy="raise")  # noqa: F821
    imagenes: Mapped[list["ReporteImagen"]] = relationship(
        "ReporteImagen", back_populates="reporte", cascade="all, delete-orphan", lazy="raise"
    )
    validaciones: Mapped[list["ReporteValidacion"]] = relationship(
        "ReporteValidacion", back_populates="reporte", lazy="raise"
    )


class ReporteImagen(Base):
    __tablename__ = "reporte_imagenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reportes.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(Text)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    reporte: Mapped["Reporte"] = relationship("Reporte", back_populates="imagenes", lazy="raise")


class ReporteValidacion(Base):
    __tablename__ = "reporte_validaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reportes.id"))
    admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    decision: Mapped[DecisionValidacion] = mapped_column(SAEnum(DecisionValidacion, name="decision_validacion"))
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    validated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    reporte: Mapped["Reporte"] = relationship("Reporte", back_populates="validaciones", lazy="raise")
    admin: Mapped["User"] = relationship("User", foreign_keys=[admin_id], lazy="raise")  # noqa: F821
