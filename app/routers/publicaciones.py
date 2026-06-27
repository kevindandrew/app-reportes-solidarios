import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_entidad_or_admin
from app.models.publicacion import TipoPublicacion
from app.schemas import ok, paginated
from app.schemas.publicacion import (
    CambiarEstadoRequest,
    PublicacionCreate,
    PublicacionOut,
    PublicacionUpdate,
)
from app.services import publicacion_service
from app.services.cloudinary_service import upload_image

router = APIRouter(prefix="/publicaciones", tags=["Publicaciones"])


@router.get("")
async def list_publicaciones(
    page: int = 1,
    limit: int = 20,
    tipo: TipoPublicacion | None = None,
    entidad_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    items, total = await publicacion_service.list_publicaciones(db, page, limit, tipo, entidad_id)
    return paginated([PublicacionOut.model_validate(i) for i in items], total, page, limit)


@router.post("")
async def create_publicacion(
    data: PublicacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_entidad_or_admin),
):
    pub = await publicacion_service.create_publicacion(db, data, current_user.id)
    return ok(PublicacionOut.model_validate(pub), "Publicación creada")


@router.get("/{pub_id}")
async def get_publicacion(pub_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    pub = await publicacion_service.get_publicacion(db, pub_id)
    return ok(PublicacionOut.model_validate(pub))


@router.put("/{pub_id}")
async def update_publicacion(
    pub_id: uuid.UUID,
    data: PublicacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    pub = await publicacion_service.update_publicacion(db, pub_id, data, current_user)
    return ok(PublicacionOut.model_validate(pub), "Publicación actualizada")


@router.delete("/{pub_id}")
async def delete_publicacion(
    pub_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    await publicacion_service.delete_publicacion(db, pub_id, current_user)
    return ok(message="Publicación eliminada")


@router.post("/{pub_id}/imagenes")
async def agregar_imagen(
    pub_id: uuid.UUID,
    file: UploadFile = File(..., description="Imagen a subir (jpg, png, webp)"),
    orden: int = Form(0),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    file_bytes = await file.read()
    url = await upload_image(file_bytes, folder="publicaciones")
    imagen = await publicacion_service.agregar_imagen(db, pub_id, url, orden)
    return ok({"id": str(imagen.id), "url": imagen.url, "orden": imagen.orden}, "Imagen subida a Cloudinary")


@router.delete("/{pub_id}/imagenes/{imagen_id}")
async def eliminar_imagen(
    pub_id: uuid.UUID,
    imagen_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    await publicacion_service.eliminar_imagen(db, pub_id, imagen_id)
    return ok(message="Imagen eliminada")


@router.patch("/{pub_id}/estado")
async def cambiar_estado(
    pub_id: uuid.UUID,
    data: CambiarEstadoRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    pub = await publicacion_service.cambiar_estado(db, pub_id, data, current_user)
    return ok(PublicacionOut.model_validate(pub), "Estado actualizado")
