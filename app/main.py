import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth, entidades, publicaciones, puntos, reportes, users, verificacion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Reportes Solidarios",
    description="API para reportes de personas/animales desaparecidos, accidentes, vulnerabilidades y publicaciones institucionales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"success": False, "data": None, "message": "Recurso no encontrado"},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "data": exc.errors(), "message": "Error de validación"},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error(f"Error inesperado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "data": None, "message": "Error interno del servidor"},
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(entidades.router)
app.include_router(reportes.router)
app.include_router(publicaciones.router)
app.include_router(puntos.router)
app.include_router(verificacion.router)


@app.get("/", tags=["Health"])
async def root():
    return {"success": True, "data": None, "message": "API Reportes Solidarios funcionando"}


@app.get("/health", tags=["Health"])
async def health():
    return {"success": True, "data": {"status": "ok"}, "message": "Servicio disponible"}
