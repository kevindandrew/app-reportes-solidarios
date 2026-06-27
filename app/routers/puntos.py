import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.schemas import ok, paginated
from app.schemas.puntos import (
    AsignarPuntosRequest,
    CanjeCreate,
    CanjeOut,
    PuntosTransaccionOut,
    RecompensaCreate,
    RecompensaOut,
    RecompensaUpdate,
)
from app.services import puntos_service

router = APIRouter(tags=["Puntos y Recompensas"])


@router.get("/recompensas")
async def list_recompensas(page: int = 1, limit: int = 20, db: AsyncSession = Depends(get_db)):
    items, total = await puntos_service.list_recompensas(db, page, limit)
    return paginated([RecompensaOut.model_validate(i) for i in items], total, page, limit)


@router.post("/recompensas")
async def create_recompensa(
    data: RecompensaCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    r = await puntos_service.create_recompensa(db, data)
    return ok(RecompensaOut.model_validate(r), "Recompensa creada")


@router.put("/recompensas/{recompensa_id}")
async def update_recompensa(
    recompensa_id: uuid.UUID,
    data: RecompensaUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    r = await puntos_service.update_recompensa(db, recompensa_id, data)
    return ok(RecompensaOut.model_validate(r), "Recompensa actualizada")


@router.delete("/recompensas/{recompensa_id}")
async def deactivate_recompensa(
    recompensa_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    r = await puntos_service.deactivate_recompensa(db, recompensa_id)
    return ok(RecompensaOut.model_validate(r), "Recompensa desactivada")


@router.post("/puntos/asignar")
async def asignar_puntos(
    data: AsignarPuntosRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    t = await puntos_service.asignar_puntos(db, data, current_user.id)
    return ok(PuntosTransaccionOut.model_validate(t), "Puntos asignados")


@router.post("/canjes")
async def canjear(
    data: CanjeCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    canje = await puntos_service.canjear(db, data, current_user.id)
    return ok(CanjeOut.model_validate(canje), "Canje realizado exitosamente")


@router.get("/canjes")
async def list_canjes(
    page: int = 1, limit: int = 20, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    items, total = await puntos_service.list_canjes_pendientes(db, page, limit)
    return paginated([CanjeOut.model_validate(i) for i in items], total, page, limit)


@router.patch("/canjes/{canje_id}/entregar")
async def entregar_canje(
    canje_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    canje = await puntos_service.entregar_canje(db, canje_id)
    return ok(CanjeOut.model_validate(canje), "Canje marcado como entregado")
