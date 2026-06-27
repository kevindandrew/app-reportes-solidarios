from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entidad import Entidad
from app.models.publicacion import EstadoPublicacionPub, Publicacion, TipoPublicacion
from app.models.user import User

PUBLICACIONES_DATA = [
    {
        "entidad_nombre": "PetCare Bolivia",
        "autor_email": "veterinaria@app.com",
        "tipo_publicacion": TipoPublicacion.campana,
        "titulo": "Campaña de vacunación gratuita",
        "contenido": "PetCare Bolivia organiza campaña de vacunación gratuita para mascotas este fin de semana.",
        "estado": EstadoPublicacionPub.publicado,
        "fecha_evento": datetime.now(timezone.utc) + timedelta(days=7),
        "lugar_evento": "PetCare Bolivia, Av. Arce #1234",
        "cupos_disponibles": 100,
    },
    {
        "entidad_nombre": "PetCare Bolivia",
        "autor_email": "veterinaria@app.com",
        "tipo_publicacion": TipoPublicacion.adopcion,
        "titulo": "Perrito mestizo en adopción",
        "contenido": "Cachorro mestizo de 3 meses busca hogar amoroso. Vacunado y desparasitado.",
        "estado": EstadoPublicacionPub.publicado,
        "especie_mascota": "Perro",
        "raza_mascota": "Mestizo",
        "edad_mascota": 3,
        "sexo_mascota": "macho",
        "castrado": False,
    },
    {
        "entidad_nombre": "Clínica Sur",
        "autor_email": "hospital@app.com",
        "tipo_publicacion": TipoPublicacion.evento,
        "titulo": "Feria de salud gratuita",
        "contenido": "Clínica Sur ofrece consultas médicas gratuitas en feria de salud comunitaria.",
        "estado": EstadoPublicacionPub.publicado,
        "fecha_evento": datetime.now(timezone.utc) + timedelta(days=14),
        "lugar_evento": "Plaza Murillo, La Paz",
        "cupos_disponibles": 200,
    },
    {
        "entidad_nombre": "Clínica Sur",
        "autor_email": "hospital@app.com",
        "tipo_publicacion": TipoPublicacion.voluntariado,
        "titulo": "Voluntarios para jornada médica",
        "contenido": "Se buscan voluntarios para apoyar en jornada médica en comunidades rurales.",
        "estado": EstadoPublicacionPub.publicado,
        "fecha_evento": datetime.now(timezone.utc) + timedelta(days=21),
        "lugar_evento": "Comunidades rurales, La Paz",
        "cupos_disponibles": 20,
    },
    {
        "entidad_nombre": "Policía Departamental",
        "autor_email": "policia@app.com",
        "tipo_publicacion": TipoPublicacion.evento,
        "titulo": "Reunión comunitaria de seguridad",
        "contenido": "La Policía Departamental invita a la comunidad a participar en reunión de seguridad vecinal.",
        "estado": EstadoPublicacionPub.publicado,
        "fecha_evento": datetime.now(timezone.utc) + timedelta(days=3),
        "lugar_evento": "Jefatura Departamental, La Paz",
        "cupos_disponibles": None,
    },
    {
        "entidad_nombre": "Policía Departamental",
        "autor_email": "policia@app.com",
        "tipo_publicacion": TipoPublicacion.campana,
        "titulo": "Campaña de prevención de robos",
        "contenido": "Consejos de seguridad para prevenir robos en época navideña.",
        "estado": EstadoPublicacionPub.publicado,
    },
]


async def seed_publicaciones(db: AsyncSession):
    for data in PUBLICACIONES_DATA:
        result = await db.execute(select(Publicacion).where(Publicacion.titulo == data["titulo"]))
        if result.scalar_one_or_none() is not None:
            continue

        entidad_result = await db.execute(
            select(Entidad).where(Entidad.nombre == data.pop("entidad_nombre"))
        )
        entidad = entidad_result.scalar_one()

        autor_result = await db.execute(select(User).where(User.email == data.pop("autor_email")))
        autor = autor_result.scalar_one()

        pub = Publicacion(autor_id=autor.id, entidad_id=entidad.id, **data)
        db.add(pub)

    await db.commit()
    print("[OK] Publicaciones creadas")
