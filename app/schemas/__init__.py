from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str = "OK"


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    pages: int = 1
    message: str = "OK"


def ok(data: Any = None, message: str = "OK") -> dict:
    return {"success": True, "data": data, "message": message}


def paginated(items: list, total: int, page: int, limit: int, message: str = "OK") -> dict:
    pages = max(1, -(-total // limit))
    return {"success": True, "data": items, "total": total, "page": page, "limit": limit, "pages": pages, "message": message}
