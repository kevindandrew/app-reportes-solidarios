import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.puntos import Canje, PuntosTransaccion
from app.models.reporte import Reporte
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import hash_password


async def get_user_by_id(db: AsyncSession, user_id: str | uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        password_hash=hash_password(data.password),
        telefono=data.telefono,
        foto_url=data.foto_url,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def list_users(db: AsyncSession, page: int, limit: int) -> tuple[list[User], int]:
    offset = (page - 1) * limit
    total_result = await db.execute(select(func.count()).select_from(User))
    total = total_result.scalar_one()
    result = await db.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all(), total


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        if field == "password":
            setattr(user, "password_hash", hash_password(value))
        else:
            setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(db: AsyncSession, user: User) -> User:
    user.activo = False
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_puntos(db: AsyncSession, user_id: uuid.UUID, page: int, limit: int):
    offset = (page - 1) * limit
    total_result = await db.execute(
        select(func.count()).select_from(PuntosTransaccion).where(PuntosTransaccion.user_id == user_id)
    )
    total = total_result.scalar_one()
    result = await db.execute(
        select(PuntosTransaccion)
        .where(PuntosTransaccion.user_id == user_id)
        .order_by(PuntosTransaccion.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total


async def get_user_reportes(db: AsyncSession, user_id: uuid.UUID, page: int, limit: int):
    offset = (page - 1) * limit
    total_result = await db.execute(
        select(func.count()).select_from(Reporte).where(Reporte.creador_id == user_id)
    )
    total = total_result.scalar_one()
    result = await db.execute(
        select(Reporte)
        .where(Reporte.creador_id == user_id)
        .options(selectinload(Reporte.imagenes))
        .order_by(Reporte.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total


async def get_user_canjes(db: AsyncSession, user_id: uuid.UUID, page: int, limit: int):
    offset = (page - 1) * limit
    total_result = await db.execute(
        select(func.count()).select_from(Canje).where(Canje.user_id == user_id)
    )
    total = total_result.scalar_one()
    result = await db.execute(
        select(Canje)
        .where(Canje.user_id == user_id)
        .order_by(Canje.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total
