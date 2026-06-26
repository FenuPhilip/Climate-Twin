"""Climate observation and region repositories."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ClimateObservation, Region, DigitalTwinState, ClimateForecast, ClimateAlert
from app.repositories.base_repository import BaseRepository


class RegionRepository(BaseRepository[Region]):
    def __init__(self, db: AsyncSession):
        super().__init__(Region, db)

    async def get_states(self) -> List[Region]:
        result = await self.db.execute(
            select(Region).where(Region.region_type == "state").order_by(Region.name)
        )
        return list(result.scalars().all())

    async def get_districts_by_state(self, state_code: str) -> List[Region]:
        result = await self.db.execute(
            select(Region)
            .where(and_(Region.region_type == "district", Region.state_code == state_code))
            .order_by(Region.name)
        )
        return list(result.scalars().all())

    async def search_by_name(self, name: str) -> List[Region]:
        result = await self.db.execute(
            select(Region).where(Region.name.ilike(f"%{name}%")).limit(20)
        )
        return list(result.scalars().all())


class ClimateObservationRepository(BaseRepository[ClimateObservation]):
    def __init__(self, db: AsyncSession):
        super().__init__(ClimateObservation, db)

    async def get_latest_by_region(self, region_id: int) -> Optional[ClimateObservation]:
        result = await self.db.execute(
            select(ClimateObservation)
            .where(ClimateObservation.region_id == region_id)
            .order_by(desc(ClimateObservation.observed_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_time_series(
        self,
        region_id: int,
        parameter: str,
        start: datetime,
        end: datetime,
        source: Optional[str] = None,
    ) -> List[ClimateObservation]:
        conditions = [
            ClimateObservation.region_id == region_id,
            ClimateObservation.observed_at.between(start, end),
        ]
        if source:
            conditions.append(ClimateObservation.source == source)

        result = await self.db.execute(
            select(ClimateObservation)
            .where(and_(*conditions))
            .order_by(ClimateObservation.observed_at)
        )
        return list(result.scalars().all())

    async def get_all_latest(self, limit: int = 500) -> List[ClimateObservation]:
        """Get latest observation per region for map rendering."""
        # Subquery: max observed_at per region
        subq = (
            select(
                ClimateObservation.region_id,
                func.max(ClimateObservation.observed_at).label("max_time"),
            )
            .group_by(ClimateObservation.region_id)
            .subquery()
        )
        result = await self.db.execute(
            select(ClimateObservation).join(
                subq,
                and_(
                    ClimateObservation.region_id == subq.c.region_id,
                    ClimateObservation.observed_at == subq.c.max_time,
                ),
            ).limit(limit)
        )
        return list(result.scalars().all())


class DigitalTwinRepository(BaseRepository[DigitalTwinState]):
    def __init__(self, db: AsyncSession):
        super().__init__(DigitalTwinState, db)

    async def get_current_state(self, region_id: int) -> Optional[DigitalTwinState]:
        result = await self.db.execute(
            select(DigitalTwinState)
            .where(DigitalTwinState.region_id == region_id)
            .order_by(desc(DigitalTwinState.valid_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_current_states(self) -> List[DigitalTwinState]:
        """Get current twin state for all regions (for map)."""
        subq = (
            select(
                DigitalTwinState.region_id,
                func.max(DigitalTwinState.valid_at).label("max_valid"),
            )
            .group_by(DigitalTwinState.region_id)
            .subquery()
        )
        result = await self.db.execute(
            select(DigitalTwinState).join(
                subq,
                and_(
                    DigitalTwinState.region_id == subq.c.region_id,
                    DigitalTwinState.valid_at == subq.c.max_valid,
                ),
            )
        )
        return list(result.scalars().all())


class ForecastRepository(BaseRepository[ClimateForecast]):
    def __init__(self, db: AsyncSession):
        super().__init__(ClimateForecast, db)

    async def get_forecasts_for_region(
        self, region_id: int, horizon_days: int
    ) -> List[ClimateForecast]:
        result = await self.db.execute(
            select(ClimateForecast)
            .where(
                and_(
                    ClimateForecast.region_id == region_id,
                    ClimateForecast.horizon_days == horizon_days,
                )
            )
            .order_by(ClimateForecast.forecast_for)
        )
        return list(result.scalars().all())


class AlertRepository(BaseRepository[ClimateAlert]):
    def __init__(self, db: AsyncSession):
        super().__init__(ClimateAlert, db)

    async def get_active_alerts(self) -> List[ClimateAlert]:
        result = await self.db.execute(
            select(ClimateAlert)
            .where(ClimateAlert.is_active == True)
            .order_by(desc(ClimateAlert.issued_at))
        )
        return list(result.scalars().all())

    async def get_alerts_by_region(self, region_id: int) -> List[ClimateAlert]:
        result = await self.db.execute(
            select(ClimateAlert)
            .where(
                and_(
                    ClimateAlert.region_id == region_id,
                    ClimateAlert.is_active == True,
                )
            )
        )
        return list(result.scalars().all())
