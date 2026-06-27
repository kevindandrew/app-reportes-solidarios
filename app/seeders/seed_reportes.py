from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reporte import (
    EstadoPublicacionReporte,
    EstadoResolucion,
    Reporte,
    SubtipoAccidente,
    TipoReporte,
)
from app.models.user import User

REPORTES_DATA = [
    {
        "titulo": "Se busca a Juan Pérez",
        "descripcion": "Hombre de 45 años desapareció el viernes en el mercado central.",
        "tipo_reporte": TipoReporte.persona_desaparecida,
        "nombre_desaparecido": "Juan Pérez",
        "edad": 45,
        "ultima_ubicacion": "Mercado Central, La Paz",
        "estado_publicacion": EstadoPublicacionReporte.pendiente,
        "estado_resolucion": EstadoResolucion.activo,
        "creador_email": "user1@app.com",
    },
    {
        "titulo": "María García encontrada",
        "descripcion": "Niña de 8 años desapareció pero fue encontrada sana y salva.",
        "tipo_reporte": TipoReporte.persona_desaparecida,
        "nombre_desaparecido": "María García",
        "edad": 8,
        "ultima_ubicacion": "Zona Sur, La Paz",
        "estado_publicacion": EstadoPublicacionReporte.aceptado,
        "estado_resolucion": EstadoResolucion.encontrado,
        "encontrado": True,
        "creador_email": "user2@app.com",
    },
    {
        "titulo": "Perro labrador perdido",
        "descripcion": "Labrador dorado, collar azul, responde al nombre de Max.",
        "tipo_reporte": TipoReporte.animal_desaparecido,
        "nombre_desaparecido": "Max",
        "raza_especie": "Labrador dorado",
        "color_descripcion": "Dorado con collar azul",
        "ultima_ubicacion": "Miraflores, La Paz",
        "estado_publicacion": EstadoPublicacionReporte.pendiente,
        "estado_resolucion": EstadoResolucion.activo,
        "creador_email": "user3@app.com",
    },
    {
        "titulo": "Gata siamesa desaparecida",
        "descripcion": "Gata siamesa de 3 años, ojos azules.",
        "tipo_reporte": TipoReporte.animal_desaparecido,
        "nombre_desaparecido": "Luna",
        "raza_especie": "Siamesa",
        "color_descripcion": "Crema con puntos oscuros",
        "ultima_ubicacion": "Sopocachi, La Paz",
        "estado_publicacion": EstadoPublicacionReporte.aceptado,
        "estado_resolucion": EstadoResolucion.activo,
        "creador_email": "user4@app.com",
    },
    {
        "titulo": "Atropello en Av. Montes",
        "descripcion": "Vehículo atropelló a peatón en el cruce de Av. Montes con Calle Loayza.",
        "tipo_reporte": TipoReporte.accidente,
        "subtipo_accidente": SubtipoAccidente.atropello,
        "ultima_ubicacion": "Av. Montes con Calle Loayza, La Paz",
        "latitud": -16.4897,
        "longitud": -68.1193,
        "estado_publicacion": EstadoPublicacionReporte.aceptado,
        "estado_resolucion": EstadoResolucion.atendido,
        "creador_email": "user5@app.com",
    },
    {
        "titulo": "Deslizamiento en zona norte",
        "descripcion": "Desastre natural afectó varias familias en la zona norte.",
        "tipo_reporte": TipoReporte.accidente,
        "subtipo_accidente": SubtipoAccidente.desastre_natural,
        "ultima_ubicacion": "Zona Norte, La Paz",
        "estado_publicacion": EstadoPublicacionReporte.aceptado,
        "estado_resolucion": EstadoResolucion.activo,
        "creador_email": "user1@app.com",
    },
    {
        "titulo": "Bache peligroso en calle principal",
        "descripcion": "Gran bache en la calle principal sin señalización, riesgo de accidente.",
        "tipo_reporte": TipoReporte.vulnerabilidad,
        "descripcion_vulnerabilidad": "Bache de aprox. 1m de diámetro y 30cm de profundidad.",
        "ultima_ubicacion": "Calle Illampu #500, La Paz",
        "estado_publicacion": EstadoPublicacionReporte.pendiente,
        "estado_resolucion": EstadoResolucion.activo,
        "creador_email": "user2@app.com",
    },
    {
        "titulo": "Luminaria rota en parque",
        "descripcion": "Luminaria rota en parque público genera zona de peligro nocturna.",
        "tipo_reporte": TipoReporte.vulnerabilidad,
        "descripcion_vulnerabilidad": "3 luminarias rotas en el parque central, zona oscura de noche.",
        "ultima_ubicacion": "Parque Central, Sopocachi",
        "estado_publicacion": EstadoPublicacionReporte.aceptado,
        "estado_resolucion": EstadoResolucion.activo,
        "creador_email": "user3@app.com",
    },
]


async def seed_reportes(db: AsyncSession):
    for data in REPORTES_DATA:
        result = await db.execute(select(Reporte).where(Reporte.titulo == data["titulo"]))
        if result.scalar_one_or_none() is not None:
            continue

        user_result = await db.execute(select(User).where(User.email == data.pop("creador_email")))
        user = user_result.scalar_one()

        fecha_desaparicion = datetime.now(timezone.utc) - timedelta(days=5)
        reporte = Reporte(
            creador_id=user.id,
            fecha_desaparicion=fecha_desaparicion if data["tipo_reporte"] in (TipoReporte.persona_desaparecida, TipoReporte.animal_desaparecido) else None,
            encontrado=data.pop("encontrado", False),
            **{k: v for k, v in data.items()},
        )
        db.add(reporte)

    await db.commit()
    print("[OK] Reportes creados")
