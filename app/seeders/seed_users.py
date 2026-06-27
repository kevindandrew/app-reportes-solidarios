from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RolUsuario, User
from app.services.auth_service import hash_password

USERS_DATA = [
    {
        "nombre": "Admin",
        "apellido": "Sistema",
        "email": "admin@app.com",
        "password": "admin123",
        "rol": RolUsuario.administrador,
    },
    {
        "nombre": "Veterinaria",
        "apellido": "PetCare",
        "email": "veterinaria@app.com",
        "password": "pass123",
        "rol": RolUsuario.entidad,
    },
    {
        "nombre": "Hospital",
        "apellido": "Clinica Sur",
        "email": "hospital@app.com",
        "password": "pass123",
        "rol": RolUsuario.entidad,
    },
    {
        "nombre": "Policia",
        "apellido": "Departamental",
        "email": "policia@app.com",
        "password": "pass123",
        "rol": RolUsuario.entidad,
    },
    {"nombre": "Usuario", "apellido": "Uno", "email": "user1@app.com", "password": "pass123", "rol": RolUsuario.usuario},
    {"nombre": "Usuario", "apellido": "Dos", "email": "user2@app.com", "password": "pass123", "rol": RolUsuario.usuario},
    {"nombre": "Usuario", "apellido": "Tres", "email": "user3@app.com", "password": "pass123", "rol": RolUsuario.usuario},
    {"nombre": "Usuario", "apellido": "Cuatro", "email": "user4@app.com", "password": "pass123", "rol": RolUsuario.usuario},
    {"nombre": "Usuario", "apellido": "Cinco", "email": "user5@app.com", "password": "pass123", "rol": RolUsuario.usuario},
]


async def seed_users(db: AsyncSession):
    for data in USERS_DATA:
        result = await db.execute(select(User).where(User.email == data["email"]))
        if result.scalar_one_or_none() is None:
            user = User(
                nombre=data["nombre"],
                apellido=data["apellido"],
                email=data["email"],
                password_hash=hash_password(data["password"]),
                rol=data["rol"],
            )
            db.add(user)
    await db.commit()
    print("[OK] Usuarios creados")
