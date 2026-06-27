from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import ok
from app.schemas.user import LoginRequest, RefreshRequest, TokenOut, UserCreate, UserOut
from app.services.auth_service import create_access_token, create_refresh_token, decode_token, verify_password
from app.services.user_service import create_user, get_user_by_email, get_user_by_id

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, data)
    return ok(UserOut.model_validate(user), "Usuario registrado exitosamente")


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario desactivado")
    token_data = {"sub": str(user.id)}
    return ok(
        TokenOut(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        ),
        "Sesión iniciada",
    )


@router.post("/refresh")
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = await get_user_by_id(db, user_id)
    if not user or not user.activo:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    token_data = {"sub": str(user.id)}
    return ok(
        TokenOut(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        ),
        "Token renovado",
    )


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return ok(UserOut.model_validate(current_user), "Datos del usuario autenticado")
