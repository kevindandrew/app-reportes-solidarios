import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.publicacion import EstadoPublicacionPub, Publicacion, PublicacionImagen, TipoPublicacion
from app.models.user import User
from app.schemas.publicacion import CambiarEstadoRequest, PublicacionCreate, PublicacionUpdate


async def _load_pub(db: AsyncSession, pub_id: uuid.UUID) -> Publicacion:
    result = await db.execute(
        select(Publicacion).where(Publicacion.id == pub_id).options(selectinload(Publicacion.imagenes))
    )
    pub = result.scalar_one_or_none()
    if not pub:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return pub


async def list_publicaciones(
    db: AsyncSession,
    page: int,
    limit: int,
    tipo: TipoPublicacion | None = None,
    entidad_id: uuid.UUID | None = None,
):
    offset = (page - 1) * limit
    query = select(Publicacion).where(Publicacion.estado == EstadoPublicacionPub.publicado)
    count_q = select(func.count()).select_from(Publicacion).where(Publicacion.estado == EstadoPublicacionPub.publicado)
    if tipo:
        query = query.where(Publicacion.tipo_publicacion == tipo)
        count_q = count_q.where(Publicacion.tipo_publicacion == tipo)
    if entidad_id:
        query = query.where(Publicacion.entidad_id == entidad_id)
        count_q = count_q.where(Publicacion.entidad_id == entidad_id)
    total = (await db.execute(count_q)).scalar_one()
    result = await db.execute(
        query.options(selectinload(Publicacion.imagenes)).order_by(Publicacion.created_at.desc()).offset(offset).limit(limit)
    )
    return result.scalars().all(), total


async def get_publicacion(db: AsyncSession, pub_id: uuid.UUID) -> Publicacion:
    return await _load_pub(db, pub_id)


async def create_publicacion(db: AsyncSession, data: PublicacionCreate, autor_id: uuid.UUID) -> Publicacion:
    pub = Publicacion(**data.model_dump(), autor_id=autor_id)
    db.add(pub)
    await db.commit()
    await db.refresh(pub)
    return await _load_pub(db, pub.id)


async def update_publicacion(
    db: AsyncSession, pub_id: uuid.UUID, data: PublicacionUpdate, current_user: User
) -> Publicacion:
    pub = await _load_pub(db, pub_id)
    from app.models.user import RolUsuario

    if pub.autor_id != current_user.id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta publicación")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(pub, field, value)
    await db.commit()
    return await _load_pub(db, pub_id)


async def delete_publicacion(db: AsyncSession, pub_id: uuid.UUID, current_user: User):
    pub = await _load_pub(db, pub_id)
    from app.models.user import RolUsuario

    if pub.autor_id != current_user.id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta publicación")
    await db.delete(pub)
    await db.commit()


async def agregar_imagen(db: AsyncSession, pub_id: uuid.UUID, url: str, orden: int = 0) -> PublicacionImagen:
    await _load_pub(db, pub_id)
    imagen = PublicacionImagen(publicacion_id=pub_id, url=url, orden=orden)
    db.add(imagen)
    await db.commit()
    await db.refresh(imagen)
    return imagen


async def eliminar_imagen(db: AsyncSession, pub_id: uuid.UUID, imagen_id: uuid.UUID):
    result = await db.execute(
        select(PublicacionImagen).where(PublicacionImagen.id == imagen_id, PublicacionImagen.publicacion_id == pub_id)
    )
    imagen = result.scalar_one_or_none()
    if not imagen:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    await db.delete(imagen)
    await db.commit()


async def cambiar_estado(
    db: AsyncSession, pub_id: uuid.UUID, data: CambiarEstadoRequest, current_user: User
) -> Publicacion:
    pub = await _load_pub(db, pub_id)
    from app.models.user import RolUsuario

    if pub.autor_id != current_user.id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    pub.estado = data.estado
    await db.commit()
    return await _load_pub(db, pub_id)
