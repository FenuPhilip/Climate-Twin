"""
ClimateTwin India — FastAPI Application Entry Point
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import engine, Base
from app.routes import (
    auth,
    climate,
    digital_twin,
    simulation,
    forecast,
    analytics,
    datasets,
    health,
    assistant,
)

configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan: startup and shutdown."""
    logger.info("ClimateTwin India starting up", version=settings.APP_VERSION)

    # Initialize Digital Twin background scheduler
    from app.services.twin_scheduler import TwinScheduler
    scheduler = TwinScheduler()
    await scheduler.start()

    yield

    logger.info("ClimateTwin India shutting down")
    await scheduler.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ClimateTwin India — AI-Powered Digital Twin API",
        description=(
            "RESTful API for the AI-Powered Digital Twin of India's Climate System. "
            "Integrates IMD, INSAT, and MOSDAC data sources to maintain a continuously "
            "evolving virtual replica of India's climate."
        ),
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # --- Routers ---
    api_prefix = "/api/v1"
    app.include_router(health.router, prefix="/api", tags=["Health"])
    app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    app.include_router(climate.router, prefix=f"{api_prefix}/climate", tags=["Climate Data"])
    app.include_router(digital_twin.router, prefix=f"{api_prefix}/twin", tags=["Digital Twin"])
    app.include_router(simulation.router, prefix=f"{api_prefix}/simulation", tags=["Simulation"])
    app.include_router(forecast.router, prefix=f"{api_prefix}/forecast", tags=["Forecast"])
    app.include_router(analytics.router, prefix=f"{api_prefix}/analytics", tags=["Analytics"])
    app.include_router(datasets.router, prefix=f"{api_prefix}/datasets", tags=["Datasets"])
    app.include_router(assistant.router, prefix=f"{api_prefix}/assistant", tags=["AI Assistant"])

    return app


app = create_app()
