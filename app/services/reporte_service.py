import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.puntos import PuntosTransaccion, TipoPunto
from app.models.reporte import (
    DecisionValidacion,
    EstadoPublicacionReporte,
    EstadoResolucion,
    Reporte,
    ReporteImagen,
    ReporteValidacion,
    TipoReporte,
)
from app.models.user import User
from app.schemas.reporte import MarcarEncontradoRequest, ReporteCreate, ReporteUpdate, ReporteValidacionCreate


async def _load_reporte(db: AsyncSession, reporte_id: uuid.UUID) -> Reporte:
    result = await db.execute(
        select(Reporte).where(Reporte.id == reporte_id).options(selectinload(Reporte.imagenes))
    )
    reporte = result.scalar_one_or_none()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return reporte


async def list_reportes(
    db: AsyncSession,
    page: int,
    limit: int,
    tipo: TipoReporte | None = None,
    estado_resolucion: EstadoResolucion | None = None,
):
    offset = (page - 1) * limit
    query = select(Reporte).where(Reporte.estado_publicacion == EstadoPublicacionReporte.aceptado)
    count_query = select(func.count()).select_from(Reporte).where(
        Reporte.estado_publicacion == EstadoPublicacionReporte.aceptado
    )
    if tipo:
        query = query.where(Reporte.tipo_reporte == tipo)
        count_query = count_query.where(Reporte.tipo_reporte == tipo)
    if estado_resolucion:
        query = query.where(Reporte.estado_resolucion == estado_resolucion)
        count_query = count_query.where(Reporte.estado_resolucion == estado_resolucion)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(
        query.options(selectinload(Reporte.imagenes)).order_by(Reporte.created_at.desc()).offset(offset).limit(limit)
    )
    return result.scalars().all(), total


async def get_reporte(db: AsyncSession, reporte_id: uuid.UUID) -> Reporte:
    return await _load_reporte(db, reporte_id)


async def create_reporte(db: AsyncSession, data: ReporteCreate, creador_id: uuid.UUID) -> Reporte:
    reporte = Reporte(**data.model_dump(), creador_id=creador_id)
    db.add(reporte)
    await db.commit()
    await db.refresh(reporte)
    return await _load_reporte(db, reporte.id)


async def update_reporte(db: AsyncSession, reporte_id: uuid.UUID, data: ReporteUpdate, current_user: User) -> Reporte:
    reporte = await _load_reporte(db, reporte_id)
    from app.models.user import RolUsuario

    if reporte.creador_id != current_user.id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este reporte")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(reporte, field, value)
    await db.commit()
    return await _load_reporte(db, reporte_id)


async def delete_reporte(db: AsyncSession, reporte_id: uuid.UUID):
    reporte = await _load_reporte(db, reporte_id)
    await db.delete(reporte)
    await db.commit()


async def agregar_imagen(db: AsyncSession, reporte_id: uuid.UUID, url: str, orden: int = 0) -> ReporteImagen:
    await _load_reporte(db, reporte_id)
    imagen = ReporteImagen(reporte_id=reporte_id, url=url, orden=orden)
    db.add(imagen)
    await db.commit()
    await db.refresh(imagen)
    return imagen


async def eliminar_imagen(db: AsyncSession, reporte_id: uuid.UUID, imagen_id: uuid.UUID):
    result = await db.execute(
        select(ReporteImagen).where(ReporteImagen.id == imagen_id, ReporteImagen.reporte_id == reporte_id)
    )
    imagen = result.scalar_one_or_none()
    if not imagen:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    await db.delete(imagen)
    await db.commit()


async def marcar_encontrado(
    db: AsyncSession, reporte_id: uuid.UUID, data: MarcarEncontradoRequest, current_user: User
) -> Reporte:
    reporte = await _load_reporte(db, reporte_id)
    from app.models.user import RolUsuario

    if reporte.creador_id != current_user.id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso")

    reporte.estado_resolucion = data.estado_resolucion
    reporte.encontrado = data.estado_resolucion in (EstadoResolucion.encontrado, EstadoResolucion.atendido)
    if reporte.encontrado:
        reporte.found_at = datetime.now(timezone.utc)

    if reporte.encontrado and reporte.estado_publicacion == EstadoPublicacionReporte.aceptado:
        user_result = await db.execute(select(User).where(User.id == reporte.creador_id))
        user = user_result.scalar_one_or_none()
        if user and user.verificado:
            transaccion = PuntosTransaccion(
                user_id=reporte.creador_id,
                cantidad=settings.BONO_ENCONTRADO_PUNTOS,
                tipo=TipoPunto.bono_encontrado,
                motivo=f"Bono por reporte resuelto: {reporte.titulo}",
            )
            db.add(transaccion)
            user.puntos_totales += settings.BONO_ENCONTRADO_PUNTOS

    await db.commit()
    return await _load_reporte(db, reporte_id)


async def list_pendientes(db: AsyncSession, page: int, limit: int):
    offset = (page - 1) * limit
    count_q = select(func.count()).select_from(Reporte).where(
        Reporte.estado_publicacion == EstadoPublicacionReporte.pendiente
    )
    total = (await db.execute(count_q)).scalar_one()
    result = await db.execute(
        select(Reporte)
        .where(Reporte.estado_publicacion == EstadoPublicacionReporte.pendiente)
        .options(selectinload(Reporte.imagenes))
        .order_by(Reporte.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total


async def validar_reporte(
    db: AsyncSession, reporte_id: uuid.UUID, data: ReporteValidacionCreate, admin_id: uuid.UUID
) -> ReporteValidacion:
    reporte = await _load_reporte(db, reporte_id)
    if reporte.estado_publicacion != EstadoPublicacionReporte.pendiente:
        raise HTTPException(status_code=400, detail="El reporte no está en estado pendiente")

    reporte.estado_publicacion = (
        EstadoPublicacionReporte.aceptado
        if data.decision == DecisionValidacion.aceptado
        else EstadoPublicacionReporte.rechazado
    )

    validacion = ReporteValidacion(
        reporte_id=reporte_id,
        admin_id=admin_id,
        decision=data.decision,
        motivo_rechazo=data.motivo_rechazo,
    )
    db.add(validacion)

    if data.decision == DecisionValidacion.aceptado:
        user_result = await db.execute(select(User).where(User.id == reporte.creador_id))
        user = user_result.scalar_one_or_none()
        if user and user.verificado:
            transaccion = PuntosTransaccion(
                user_id=reporte.creador_id,
                admin_id=admin_id,
                cantidad=settings.BONO_REPORTE_PUNTOS,
                tipo=TipoPunto.bono_reporte,
                motivo=f"Bono por reporte aceptado: {reporte.titulo}",
            )
            db.add(transaccion)
            user.puntos_totales += settings.BONO_REPORTE_PUNTOS

    await db.commit()
    await db.refresh(validacion)
    return validacion


async def get_validaciones(db: AsyncSession, reporte_id: uuid.UUID, page: int, limit: int):
    await _load_reporte(db, reporte_id)
    offset = (page - 1) * limit
    total = (
        await db.execute(
            select(func.count()).select_from(ReporteValidacion).where(ReporteValidacion.reporte_id == reporte_id)
        )
    ).scalar_one()
    result = await db.execute(
        select(ReporteValidacion)
        .where(ReporteValidacion.reporte_id == reporte_id)
        .order_by(ReporteValidacion.validated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total
