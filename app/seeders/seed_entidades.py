from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entidad import Entidad, EntidadUsuario, TipoEntidad
from app.models.user import User

ENTIDADES_DATA = [
    {
        "nombre": "PetCare Bolivia",
        "tipo": TipoEntidad.veterinaria,
        "email_contacto": "contacto@petcare.bo",
        "telefono": "591-2-123456",
        "user_email": "veterinaria@app.com",
    },
    {
        "nombre": "Clínica Sur",
        "tipo": TipoEntidad.hospital,
        "email_contacto": "contacto@clinicasur.bo",
        "telefono": "591-2-234567",
        "user_email": "hospital@app.com",
    },
    {
        "nombre": "Policía Departamental",
        "tipo": TipoEntidad.policia,
        "email_contacto": "contacto@policia.bo",
        "telefono": "110",
        "user_email": "policia@app.com",
    },
]


async def seed_entidades(db: AsyncSession):
    admin_result = await db.execute(select(User).where(User.email == "admin@app.com"))
    admin = admin_result.scalar_one()

    for data in ENTIDADES_DATA:
        result = await db.execute(select(Entidad).where(Entidad.nombre == data["nombre"]))
        entidad = result.scalar_one_or_none()

        if entidad is None:
            entidad = Entidad(
                admin_creador_id=admin.id,
                nombre=data["nombre"],
                tipo=data["tipo"],
                email_contacto=data["email_contacto"],
                telefono=data["telefono"],
            )
            db.add(entidad)
            await db.flush()

        user_result = await db.execute(select(User).where(User.email == data["user_email"]))
        user = user_result.scalar_one_or_none()
        if user:
            existing = await db.execute(
                select(EntidadUsuario).where(
                    EntidadUsuario.entidad_id == entidad.id, EntidadUsuario.user_id == user.id
                )
            )
            if existing.scalar_one_or_none() is None:
                db.add(EntidadUsuario(entidad_id=entidad.id, user_id=user.id))

    await db.commit()
    print("[OK] Entidades creadas")
