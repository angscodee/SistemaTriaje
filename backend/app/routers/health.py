"""Health check endpoints"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as aioredis
from app.config import settings
from app.database import AsyncSessionLocal

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict:
    """Liveness probe - simple check that the app is running"""
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready() -> JSONResponse:
    """Readiness probe - check dependencies (DB, Redis)"""
    checks = {"postgres": False, "redis": False}

    # Check PostgreSQL
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                checks["postgres"] = True
    except Exception as e:
        checks["postgres_error"] = str(e)

    # Check Redis
    try:
        redis_client = await aioredis.from_url(settings.redis_url, encoding="utf-8")
        await redis_client.ping()
        checks["redis"] = True
        await redis_client.close()
    except Exception as e:
        checks["redis_error"] = str(e)

    # Return 200 if all checks pass, 503 otherwise
    all_ok = checks["postgres"] and checks["redis"]
    status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if all_ok else "not_ready", "checks": checks},
    )
