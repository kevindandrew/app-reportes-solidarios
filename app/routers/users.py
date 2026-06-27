import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import RolUsuario
from app.schemas import ok, paginated
from app.schemas.puntos import CanjeOut, PuntosTransaccionOut
from app.schemas.reporte import ReporteOut
from app.schemas.user import UserOut, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def list_users(
    page: int = 1, limit: int = 20, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    users, total = await user_service.list_users(db, page, limit)
    return paginated([UserOut.model_validate(u) for u in users], total, page, limit)


@router.get("/{user_id}")
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return ok(UserOut.model_validate(user))


@router.put("/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este usuario")
    if data.rol is not None and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="Solo el admin puede cambiar roles")
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    updated = await user_service.update_user(db, user, data)
    return ok(UserOut.model_validate(updated), "Usuario actualizado")


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    updated = await user_service.deactivate_user(db, user)
    return ok(UserOut.model_validate(updated), "Usuario desactivado")


@router.get("/{user_id}/puntos")
async def get_puntos(
    user_id: uuid.UUID,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    items, total = await user_service.get_user_puntos(db, user_id, page, limit)
    return paginated([PuntosTransaccionOut.model_validate(i) for i in items], total, page, limit)


@router.get("/{user_id}/reportes")
async def get_reportes(
    user_id: uuid.UUID,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items, total = await user_service.get_user_reportes(db, user_id, page, limit)
    return paginated([ReporteOut.model_validate(i) for i in items], total, page, limit)


@router.get("/{user_id}/canjes")
async def get_canjes(
    user_id: uuid.UUID,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id and current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    items, total = await user_service.get_user_canjes(db, user_id, page, limit)
    return paginated([CanjeOut.model_validate(i) for i in items], total, page, limit)
