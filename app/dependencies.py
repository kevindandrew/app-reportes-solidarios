from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    from app.services.user_service import get_user_by_id

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if user is None or not user.activo:
        raise credentials_exception
    return user


async def require_admin(current_user=Depends(get_current_user)):
    from app.models.user import RolUsuario

    if current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="Se requiere rol administrador")
    return current_user


async def require_entidad_or_admin(current_user=Depends(get_current_user)):
    from app.models.user import RolUsuario

    if current_user.rol not in (RolUsuario.administrador, RolUsuario.entidad):
        raise HTTPException(status_code=403, detail="Se requiere rol entidad o administrador")
    return current_user
