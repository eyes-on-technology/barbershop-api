"""
Aplicação principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.config import settings
from app.routers import auth, servicos, disponibilidades, agendamentos, usuarios, admin

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Criar aplicação
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Exception Handlers ====================
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error": str(exc.detail),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handler para erros de validação"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Erro de validação",
            "error": str(exc),
        },
    )


# ==================== Rotas ====================
# Incluir routers
app.include_router(auth.router)
app.include_router(servicos.router)
app.include_router(disponibilidades.router)
app.include_router(agendamentos.router)
app.include_router(usuarios.router)
app.include_router(admin.router)


# ==================== Health Check ====================
@app.get("/health")
async def health_check():
    """Verifica saúde da API"""
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": settings.api_version,
    }


@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "message": "Bem-vindo à Barbershop API",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ==================== Startup/Shutdown ====================
@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    logger.info(f"🚀 Iniciando {settings.api_title} v{settings.api_version}")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info(f"CORS habilitado para: {settings.allowed_origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação"""
    logger.info("🛑 Encerrando aplicação")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=3000,
        reload=settings.debug,
    )

