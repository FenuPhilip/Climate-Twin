"""Health and status endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.dependencies import get_db, get_redis

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "ClimateTwin India API",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.APP_ENV,
    }


@router.get("/health/detailed", tags=["Health"])
async def detailed_health(
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    services = {}

    # Check DB
    try:
        await db.execute(text("SELECT 1"))
        services["database"] = {"status": "healthy", "type": "postgresql+postgis"}
    except Exception as e:
        services["database"] = {"status": "unhealthy", "error": str(e)}

    # Check Redis
    try:
        await redis.ping()
        services["redis"] = {"status": "healthy"}
    except Exception as e:
        services["redis"] = {"status": "unhealthy", "error": str(e)}

    overall = "healthy" if all(
        s["status"] == "healthy" for s in services.values()
    ) else "degraded"

    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.APP_VERSION,
        "services": services,
    }
