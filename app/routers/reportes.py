import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.reporte import EstadoResolucion, TipoReporte
from app.schemas import ok, paginated
from app.schemas.reporte import (
    MarcarEncontradoRequest,
    ReporteCreate,
    ReporteOut,
    ReporteUpdate,
    ReporteValidacionCreate,
    ReporteValidacionOut,
)
from app.services import reporte_service
from app.services.cloudinary_service import upload_image

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/pendientes")
async def list_pendientes(
    page: int = 1, limit: int = 20, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    items, total = await reporte_service.list_pendientes(db, page, limit)
    return paginated([ReporteOut.model_validate(i) for i in items], total, page, limit)


@router.get("")
async def list_reportes(
    page: int = 1,
    limit: int = 20,
    tipo: TipoReporte | None = None,
    estado_resolucion: EstadoResolucion | None = None,
    db: AsyncSession = Depends(get_db),
):
    items, total = await reporte_service.list_reportes(db, page, limit, tipo, estado_resolucion)
    return paginated([ReporteOut.model_validate(i) for i in items], total, page, limit)


@router.post("")
async def create_reporte(
    data: ReporteCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    reporte = await reporte_service.create_reporte(db, data, current_user.id)
    return ok(ReporteOut.model_validate(reporte), "Reporte creado")


@router.get("/{reporte_id}")
async def get_reporte(reporte_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    reporte = await reporte_service.get_reporte(db, reporte_id)
    return ok(ReporteOut.model_validate(reporte))


@router.put("/{reporte_id}")
async def update_reporte(
    reporte_id: uuid.UUID,
    data: ReporteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    reporte = await reporte_service.update_reporte(db, reporte_id, data, current_user)
    return ok(ReporteOut.model_validate(reporte), "Reporte actualizado")


@router.delete("/{reporte_id}")
async def delete_reporte(
    reporte_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    await reporte_service.delete_reporte(db, reporte_id)
    return ok(message="Reporte eliminado")


@router.post("/{reporte_id}/imagenes")
async def agregar_imagen(
    reporte_id: uuid.UUID,
    file: UploadFile = File(..., description="Imagen a subir (jpg, png, webp)"),
    orden: int = Form(0),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    file_bytes = await file.read()
    url = await upload_image(file_bytes, folder="reportes")
    imagen = await reporte_service.agregar_imagen(db, reporte_id, url, orden)
    return ok({"id": str(imagen.id), "url": imagen.url, "orden": imagen.orden}, "Imagen subida a Cloudinary")


@router.delete("/{reporte_id}/imagenes/{imagen_id}")
async def eliminar_imagen(
    reporte_id: uuid.UUID,
    imagen_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    await reporte_service.eliminar_imagen(db, reporte_id, imagen_id)
    return ok(message="Imagen eliminada")


@router.patch("/{reporte_id}/encontrado")
async def marcar_encontrado(
    reporte_id: uuid.UUID,
    data: MarcarEncontradoRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    reporte = await reporte_service.marcar_encontrado(db, reporte_id, data, current_user)
    return ok(ReporteOut.model_validate(reporte), "Estado actualizado")


@router.post("/{reporte_id}/validar")
async def validar_reporte(
    reporte_id: uuid.UUID,
    data: ReporteValidacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    validacion = await reporte_service.validar_reporte(db, reporte_id, data, current_user.id)
    return ok(ReporteValidacionOut.model_validate(validacion), "Reporte validado")


@router.get("/{reporte_id}/validaciones")
async def get_validaciones(
    reporte_id: uuid.UUID,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    items, total = await reporte_service.get_validaciones(db, reporte_id, page, limit)
    return paginated([ReporteValidacionOut.model_validate(i) for i in items], total, page, limit)
