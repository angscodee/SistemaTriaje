"""FastAPI application for SistemaTriaje backend"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AppException
from app.core.security import close_redis, init_redis
from app.database import close_db
from app.routers import auth, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting up SistemaTriaje backend...")
    await init_redis()
    logger.info("Redis initialized")

    yield

    # Shutdown
    logger.info("Shutting down SistemaTriaje backend...")
    await close_redis()
    await close_db()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Sistema de triaje automático de alertas SOC para PYMEs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": type(exc).__name__},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "Sistema de triaje automático de alertas SOC para PYMEs",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }
