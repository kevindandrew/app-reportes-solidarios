import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.verificacion import EstadoVerificacion, VerificacionIdentidad
from app.schemas.verificacion import RevisarVerificacionRequest


async def solicitar_verificacion(
    db: AsyncSession, user_id: uuid.UUID, url_anverso: str, url_reverso: str
) -> VerificacionIdentidad:
    # Solo una solicitud pendiente a la vez
    existing = await db.execute(
        select(VerificacionIdentidad).where(
            VerificacionIdentidad.user_id == user_id,
            VerificacionIdentidad.estado == EstadoVerificacion.pendiente,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Ya tienes una solicitud de verificación pendiente. Espera la revisión del administrador.",
        )

    verificacion = VerificacionIdentidad(
        user_id=user_id,
        url_anverso=url_anverso,
        url_reverso=url_reverso,
    )
    db.add(verificacion)
    await db.commit()
    await db.refresh(verificacion)
    return verificacion


async def get_mi_verificacion(db: AsyncSession, user_id: uuid.UUID) -> VerificacionIdentidad | None:
    result = await db.execute(
        select(VerificacionIdentidad)
        .where(VerificacionIdentidad.user_id == user_id)
        .order_by(VerificacionIdentidad.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_pendientes(db: AsyncSession, page: int, limit: int):
    offset = (page - 1) * limit
    total = (
        await db.execute(
            select(func.count())
            .select_from(VerificacionIdentidad)
            .where(VerificacionIdentidad.estado == EstadoVerificacion.pendiente)
        )
    ).scalar_one()
    result = await db.execute(
        select(VerificacionIdentidad)
        .where(VerificacionIdentidad.estado == EstadoVerificacion.pendiente)
        .order_by(VerificacionIdentidad.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total


async def revisar_verificacion(
    db: AsyncSession,
    verificacion_id: uuid.UUID,
    data: RevisarVerificacionRequest,
    admin_id: uuid.UUID,
) -> VerificacionIdentidad:
    result = await db.execute(
        select(VerificacionIdentidad).where(VerificacionIdentidad.id == verificacion_id)
    )
    verificacion = result.scalar_one_or_none()
    if not verificacion:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if verificacion.estado != EstadoVerificacion.pendiente:
        raise HTTPException(status_code=400, detail="Esta solicitud ya fue procesada")
    if data.decision == EstadoVerificacion.pendiente:
        raise HTTPException(status_code=400, detail="La decision debe ser 'verificado' o 'rechazado'")
    if data.decision == EstadoVerificacion.rechazado and not data.motivo_rechazo:
        raise HTTPException(status_code=400, detail="Debe indicar el motivo de rechazo")

    verificacion.estado = data.decision
    verificacion.admin_id = admin_id
    verificacion.motivo_rechazo = data.motivo_rechazo

    if data.decision == EstadoVerificacion.verificado:
        user_result = await db.execute(select(User).where(User.id == verificacion.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.verificado = True

    await db.commit()
    await db.refresh(verificacion)
    return verificacion
