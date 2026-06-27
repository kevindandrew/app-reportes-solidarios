import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entidad import Entidad, EntidadUsuario
from app.models.user import User
from app.schemas.entidad import EntidadCreate, EntidadUpdate


async def list_entidades(db: AsyncSession, page: int, limit: int):
    offset = (page - 1) * limit
    total_result = await db.execute(select(func.count()).select_from(Entidad).where(Entidad.activo == True))
    total = total_result.scalar_one()
    result = await db.execute(select(Entidad).where(Entidad.activo == True).offset(offset).limit(limit))
    return result.scalars().all(), total


async def get_entidad(db: AsyncSession, entidad_id: uuid.UUID) -> Entidad:
    result = await db.execute(select(Entidad).where(Entidad.id == entidad_id))
    entidad = result.scalar_one_or_none()
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return entidad


async def create_entidad(db: AsyncSession, data: EntidadCreate, admin_id: uuid.UUID) -> Entidad:
    entidad = Entidad(**data.model_dump(), admin_creador_id=admin_id)
    db.add(entidad)
    await db.commit()
    await db.refresh(entidad)
    return entidad


async def update_entidad(db: AsyncSession, entidad: Entidad, data: EntidadUpdate) -> Entidad:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(entidad, field, value)
    await db.commit()
    await db.refresh(entidad)
    return entidad


async def deactivate_entidad(db: AsyncSession, entidad: Entidad) -> Entidad:
    entidad.activo = False
    await db.commit()
    await db.refresh(entidad)
    return entidad


async def asignar_usuario(db: AsyncSession, entidad_id: uuid.UUID, user_id: uuid.UUID) -> EntidadUsuario:
    user_result = await db.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    existing = await db.execute(
        select(EntidadUsuario).where(
            EntidadUsuario.entidad_id == entidad_id, EntidadUsuario.user_id == user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El usuario ya está asignado a esta entidad")

    eu = EntidadUsuario(entidad_id=entidad_id, user_id=user_id)
    db.add(eu)
    await db.commit()
    await db.refresh(eu)
    return eu


async def quitar_usuario(db: AsyncSession, entidad_id: uuid.UUID, user_id: uuid.UUID):
    result = await db.execute(
        select(EntidadUsuario).where(
            EntidadUsuario.entidad_id == entidad_id, EntidadUsuario.user_id == user_id
        )
    )
    eu = result.scalar_one_or_none()
    if not eu:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    await db.delete(eu)
    await db.commit()
