import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import RolUsuario
from app.schemas import ok, paginated
from app.schemas.verificacion import RevisarVerificacionRequest, VerificacionOut
from app.services import verificacion_service
from app.services.cloudinary_service import upload_image

router = APIRouter(prefix="/verificacion", tags=["Verificacion de Identidad"])


@router.post("/solicitar")
async def solicitar_verificacion(
    anverso: UploadFile = File(..., description="Foto del anverso del documento de identidad"),
    reverso: UploadFile = File(..., description="Foto del reverso del documento de identidad"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.verificado:
        raise HTTPException(status_code=400, detail="Tu cuenta ya está verificada")
    if current_user.rol != RolUsuario.usuario:
        raise HTTPException(status_code=400, detail="Solo los usuarios comunes necesitan verificacion")

    for f in (anverso, reverso):
        if not f.content_type or not f.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Ambos archivos deben ser imágenes")

    anverso_bytes = await anverso.read()
    reverso_bytes = await reverso.read()

    url_anverso = await upload_image(anverso_bytes, folder="verificaciones/anverso")
    url_reverso = await upload_image(reverso_bytes, folder="verificaciones/reverso")

    verificacion = await verificacion_service.solicitar_verificacion(
        db, current_user.id, url_anverso, url_reverso
    )
    return ok(VerificacionOut.model_validate(verificacion), "Solicitud enviada. El administrador revisará tu documento.")


@router.get("/mi-solicitud")
async def mi_solicitud(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    verificacion = await verificacion_service.get_mi_verificacion(db, current_user.id)
    if not verificacion:
        return ok(None, "No tienes solicitudes de verificación")
    return ok(VerificacionOut.model_validate(verificacion))


@router.get("/pendientes")
async def list_pendientes(
    page: int = 1, limit: int = 20, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    items, total = await verificacion_service.list_pendientes(db, page, limit)
    return paginated([VerificacionOut.model_validate(i) for i in items], total, page, limit)


@router.post("/{verificacion_id}/revisar")
async def revisar_verificacion(
    verificacion_id: uuid.UUID,
    data: RevisarVerificacionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    verificacion = await verificacion_service.revisar_verificacion(
        db, verificacion_id, data, current_user.id
    )
    msg = "Cuenta verificada exitosamente" if verificacion.estado.value == "verificado" else "Solicitud rechazada"
    return ok(VerificacionOut.model_validate(verificacion), msg)
