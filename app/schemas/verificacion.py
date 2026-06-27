import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.verificacion import EstadoVerificacion


class VerificacionOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    url_anverso: str
    url_reverso: str
    estado: EstadoVerificacion
    admin_id: uuid.UUID | None
    motivo_rechazo: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RevisarVerificacionRequest(BaseModel):
    decision: EstadoVerificacion
    motivo_rechazo: str | None = None
