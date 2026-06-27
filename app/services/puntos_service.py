import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.puntos import Canje, EstadoCanje, PuntosTransaccion, Recompensa, TipoPunto
from app.models.user import User
from app.schemas.puntos import AsignarPuntosRequest, CanjeCreate, RecompensaCreate, RecompensaUpdate


async def list_recompensas(db: AsyncSession, page: int, limit: int):
    offset = (page - 1) * limit
    total = (
        await db.execute(select(func.count()).select_from(Recompensa).where(Recompensa.activo == True))
    ).scalar_one()
    result = await db.execute(
        select(Recompensa).where(Recompensa.activo == True).offset(offset).limit(limit)
    )
    return result.scalars().all(), total


async def get_recompensa(db: AsyncSession, recompensa_id: uuid.UUID) -> Recompensa:
    result = await db.execute(select(Recompensa).where(Recompensa.id == recompensa_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Recompensa no encontrada")
    return r


async def create_recompensa(db: AsyncSession, data: RecompensaCreate) -> Recompensa:
    r = Recompensa(**data.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


async def update_recompensa(db: AsyncSession, recompensa_id: uuid.UUID, data: RecompensaUpdate) -> Recompensa:
    r = await get_recompensa(db, recompensa_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(r, field, value)
    await db.commit()
    await db.refresh(r)
    return r


async def deactivate_recompensa(db: AsyncSession, recompensa_id: uuid.UUID) -> Recompensa:
    r = await get_recompensa(db, recompensa_id)
    r.activo = False
    await db.commit()
    await db.refresh(r)
    return r


async def asignar_puntos(db: AsyncSession, data: AsignarPuntosRequest, admin_id: uuid.UUID) -> PuntosTransaccion:
    user_result = await db.execute(select(User).where(User.id == data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    transaccion = PuntosTransaccion(
        user_id=data.user_id,
        admin_id=admin_id,
        cantidad=data.cantidad,
        tipo=TipoPunto.asignacion_manual,
        motivo=data.motivo,
    )
    db.add(transaccion)
    user.puntos_totales += data.cantidad
    await db.commit()
    await db.refresh(transaccion)
    return transaccion


async def canjear(db: AsyncSession, data: CanjeCreate, user_id: uuid.UUID) -> Canje:
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user.verificado:
        raise HTTPException(
            status_code=403,
            detail="Debes verificar tu identidad antes de canjear puntos. Ve a POST /verificacion/solicitar",
        )

    recompensa = await get_recompensa(db, data.recompensa_id)
    if not recompensa.activo:
        raise HTTPException(status_code=400, detail="Recompensa no disponible")

    if user.puntos_totales < recompensa.costo_puntos:
        raise HTTPException(status_code=400, detail="Puntos insuficientes")

    if recompensa.stock != -1:
        canjes_entregados = (
            await db.execute(
                select(func.count())
                .select_from(Canje)
                .where(Canje.recompensa_id == data.recompensa_id, Canje.estado != EstadoCanje.cancelado)
            )
        ).scalar_one()
        if canjes_entregados >= recompensa.stock:
            raise HTTPException(status_code=400, detail="Stock agotado")

    transaccion = PuntosTransaccion(
        user_id=user_id,
        cantidad=-recompensa.costo_puntos,
        tipo=TipoPunto.canje,
        motivo=f"Canje: {recompensa.nombre}",
    )
    db.add(transaccion)

    canje = Canje(
        user_id=user_id,
        recompensa_id=data.recompensa_id,
        puntos_usados=recompensa.costo_puntos,
    )
    db.add(canje)
    user.puntos_totales -= recompensa.costo_puntos
    await db.commit()
    await db.refresh(canje)
    return canje


async def list_canjes_pendientes(db: AsyncSession, page: int, limit: int):
    offset = (page - 1) * limit
    total = (
        await db.execute(select(func.count()).select_from(Canje).where(Canje.estado == EstadoCanje.pendiente))
    ).scalar_one()
    result = await db.execute(
        select(Canje)
        .where(Canje.estado == EstadoCanje.pendiente)
        .order_by(Canje.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total


async def entregar_canje(db: AsyncSession, canje_id: uuid.UUID) -> Canje:
    result = await db.execute(select(Canje).where(Canje.id == canje_id))
    canje = result.scalar_one_or_none()
    if not canje:
        raise HTTPException(status_code=404, detail="Canje no encontrado")
    if canje.estado != EstadoCanje.pendiente:
        raise HTTPException(status_code=400, detail="El canje no está en estado pendiente")
    canje.estado = EstadoCanje.entregado
    canje.procesado_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(canje)
    return canje
