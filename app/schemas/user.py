import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import RolUsuario


class UserCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    telefono: str | None = None
    foto_url: str | None = None


class UserUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    email: EmailStr | None = None
    telefono: str | None = None
    foto_url: str | None = None
    password: str | None = None
    rol: RolUsuario | None = None
    activo: bool | None = None


class UserOut(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    email: str
    rol: RolUsuario
    activo: bool
    verificado: bool
    puntos_totales: int
    foto_url: str | None
    telefono: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
