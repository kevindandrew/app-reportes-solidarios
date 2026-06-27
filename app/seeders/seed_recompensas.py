from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.puntos import Recompensa

RECOMPENSAS_DATA = [
    {"nombre": "Gorra solidaria", "descripcion": "Gorra oficial de la app con logo bordado.", "costo_puntos": 500, "stock": 10},
    {"nombre": "Camiseta app", "descripcion": "Camiseta de algodón con diseño exclusivo.", "costo_puntos": 1000, "stock": 5},
    {"nombre": "Certificado digital", "descripcion": "Certificado digital de colaborador solidario.", "costo_puntos": 200, "stock": -1},
]


async def seed_recompensas(db: AsyncSession):
    for data in RECOMPENSAS_DATA:
        result = await db.execute(select(Recompensa).where(Recompensa.nombre == data["nombre"]))
        if result.scalar_one_or_none() is None:
            db.add(Recompensa(**data))
    await db.commit()
    print("[OK] Recompensas creadas")
