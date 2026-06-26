"""
Twin Scheduler — Background task that periodically updates the Digital Twin.
Uses APScheduler for async scheduling.
"""
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.services.digital_twin_engine import twin_engine

logger = structlog.get_logger()


class TwinScheduler:
    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    async def start(self):
        """Initialize and start the background scheduler."""
        # Initialize Digital Twin
        await twin_engine.initialize()

        # Schedule periodic updates
        self._scheduler.add_job(
            self._update_twin,
            trigger=IntervalTrigger(seconds=settings.TWIN_UPDATE_INTERVAL_SECONDS),
            id="twin_update",
            name="Digital Twin Update",
            replace_existing=True,
        )

        self._scheduler.start()
        logger.info(
            "Twin Scheduler started",
            interval_seconds=settings.TWIN_UPDATE_INTERVAL_SECONDS,
        )

    async def stop(self):
        """Gracefully stop the scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
        logger.info("Twin Scheduler stopped")

    @staticmethod
    async def _update_twin():
        """Periodic twin update job."""
        try:
            await twin_engine.update_all()
            logger.info("Digital Twin states updated successfully")
        except Exception as e:
            logger.error("Twin update failed", error=str(e))
