import asyncio
from functools import partial

import cloudinary
import cloudinary.uploader

from app.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


async def upload_image(file_bytes: bytes, folder: str = "general") -> str:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        partial(
            cloudinary.uploader.upload,
            file_bytes,
            folder=folder,
            resource_type="image",
        ),
    )
    return result["secure_url"]


async def delete_image(public_id: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        partial(cloudinary.uploader.destroy, public_id, resource_type="image"),
    )
