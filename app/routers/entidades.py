import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.schemas import ok, paginated
from app.schemas.entidad import AsignarUsuarioRequest, EntidadCreate, EntidadOut, EntidadUpdate, EntidadUsuarioOut
from app.services import entidad_service

router = APIRouter(prefix="/entidades", tags=["Entidades"])


@router.get("")
async def list_entidades(page: int = 1, limit: int = 20, db: AsyncSession = Depends(get_db)):
    items, total = await entidad_service.list_entidades(db, page, limit)
    return paginated([EntidadOut.model_validate(i) for i in items], total, page, limit)


@router.post("")
async def create_entidad(
    data: EntidadCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)
):
    entidad = await entidad_service.create_entidad(db, data, current_user.id)
    return ok(EntidadOut.model_validate(entidad), "Entidad creada")


@router.get("/{entidad_id}")
async def get_entidad(entidad_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    entidad = await entidad_service.get_entidad(db, entidad_id)
    return ok(EntidadOut.model_validate(entidad))


@router.put("/{entidad_id}")
async def update_entidad(
    entidad_id: uuid.UUID, data: EntidadUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    entidad = await entidad_service.get_entidad(db, entidad_id)
    updated = await entidad_service.update_entidad(db, entidad, data)
    return ok(EntidadOut.model_validate(updated), "Entidad actualizada")


@router.delete("/{entidad_id}")
async def deactivate_entidad(
    entidad_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    entidad = await entidad_service.get_entidad(db, entidad_id)
    updated = await entidad_service.deactivate_entidad(db, entidad)
    return ok(EntidadOut.model_validate(updated), "Entidad desactivada")


@router.post("/{entidad_id}/usuarios")
async def asignar_usuario(
    entidad_id: uuid.UUID,
    data: AsignarUsuarioRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    await entidad_service.get_entidad(db, entidad_id)
    eu = await entidad_service.asignar_usuario(db, entidad_id, data.user_id)
    return ok(EntidadUsuarioOut.model_validate(eu), "Usuario asignado a entidad")


@router.delete("/{entidad_id}/usuarios/{user_id}")
async def quitar_usuario(
    entidad_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    await entidad_service.quitar_usuario(db, entidad_id, user_id)
    return ok(message="Usuario removido de la entidad")
