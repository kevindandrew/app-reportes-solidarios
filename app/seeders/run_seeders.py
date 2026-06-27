import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import AsyncSessionLocal
from app.seeders.seed_users import seed_users
from app.seeders.seed_entidades import seed_entidades
from app.seeders.seed_reportes import seed_reportes
from app.seeders.seed_publicaciones import seed_publicaciones
from app.seeders.seed_recompensas import seed_recompensas


async def run():
    async with AsyncSessionLocal() as db:
        print("Ejecutando seeders...")
        await seed_users(db)
        await seed_entidades(db)
        await seed_reportes(db)
        await seed_publicaciones(db)
        await seed_recompensas(db)
        print("[OK] Todos los seeders completados")


if __name__ == "__main__":
    asyncio.run(run())
