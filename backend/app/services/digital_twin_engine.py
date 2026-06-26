"""
Digital Twin Engine — Maintains and updates the virtual climate state.

Each region maintains a continuously evolving ClimateState that reflects:
- Latest observations from IMD/INSAT/MOSDAC
- AI-predicted future states
- Derived risk indices (flood, drought, heatwave)
"""
import math
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional

import structlog

from app.services.mock_data_service import MockDataService, INDIA_STATES

logger = structlog.get_logger()


class ClimateState:
    """Virtual climate state for a single region."""

    def __init__(self, region: Dict):
        self.region = region
        self.region_id = region["id"]
        self.region_name = region["name"]
        self.last_updated = datetime.now(timezone.utc)

        # Current observed state
        self.temperature_current: Optional[float] = None
        self.rainfall_current: Optional[float] = None
        self.humidity_current: Optional[float] = None
        self.lst_current: Optional[float] = None
        self.sst_current: Optional[float] = None

        # Predicted state
        self.temperature_predicted: Optional[float] = None
        self.rainfall_predicted: Optional[float] = None
        self.prediction_confidence: float = 0.0
        self.prediction_horizon_hours: int = 24

        # Risk indices
        self.flood_risk: float = 0.0
        self.heatwave_probability: float = 0.0
        self.drought_index: float = 0.0
        self.temperature_anomaly: float = 0.0
        self.rainfall_anomaly: float = 0.0

        self.data_sources: List[str] = []
        self.model_version: str = "mock-v1.0"

        # Initialize with mock data
        self._initialize()

    def _initialize(self):
        """Seed with initial mock observation."""
        obs = MockDataService.get_current_observation(self.region)
        self._apply_observation(obs)

    def _apply_observation(self, obs: Dict):
        """Apply a new climate observation to update state."""
        self.temperature_current = obs.get("temperature_mean")
        self.rainfall_current = obs.get("rainfall")
        self.humidity_current = obs.get("humidity")
        self.lst_current = obs.get("land_surface_temp")
        self.sst_current = obs.get("sea_surface_temp")
        self.flood_risk = obs.get("flood_risk", 0.0)
        self.heatwave_probability = obs.get("heatwave_probability", 0.0)
        self.drought_index = obs.get("drought_index", 0.0)
        self.temperature_anomaly = obs.get("temperature_anomaly", 0.0)
        self.rainfall_anomaly = obs.get("rainfall_anomaly", 0.0)
        self.last_updated = datetime.now(timezone.utc)

        if "IMD_MOCK" in obs.get("source", ""):
            self.data_sources = ["IMD", "INSAT"]
        else:
            self.data_sources = [obs.get("source", "IMD")]

    def update_with_observation(self, obs: Dict):
        """Update twin state with new observation."""
        self._apply_observation(obs)
        logger.debug(
            "Twin state updated",
            region=self.region_name,
            temperature=self.temperature_current,
            rainfall=self.rainfall_current,
        )

    def apply_prediction(self, predicted_temp: float, predicted_rainfall: float, confidence: float):
        """Apply AI prediction to twin state."""
        self.temperature_predicted = predicted_temp
        self.rainfall_predicted = predicted_rainfall
        self.prediction_confidence = confidence
        logger.debug(
            "AI prediction applied to twin",
            region=self.region_name,
            temp_predicted=predicted_temp,
            rain_predicted=predicted_rainfall,
        )

    def apply_simulation_delta(
        self,
        temp_delta: float = 0.0,
        rainfall_delta_pct: float = 0.0,
        humidity_delta: float = 0.0,
    ) -> Dict:
        """
        Apply what-if scenario deltas and calculate cascading effects.
        Returns new simulated state without modifying the twin permanently.
        """
        new_temp = (self.temperature_current or 25.0) + temp_delta
        rainfall_multiplier = 1 + (rainfall_delta_pct / 100)
        new_rainfall = (self.rainfall_current or 0.0) * rainfall_multiplier
        new_humidity = min(100, max(0, (self.humidity_current or 60.0) + humidity_delta))

        # Cascade effects
        # Flood risk increases with rainfall
        flood_risk = min(1.0, (new_rainfall / 20.0) * 0.5 + (self.flood_risk or 0.0) * 0.3)

        # Heatwave probability increases with temperature
        heatwave_prob = max(0.0, (new_temp - 38) / 10) if new_temp > 38 else 0.0

        # Drought index: low rainfall → high drought
        drought = max(0.0, 1.0 - (new_rainfall / max(1.0, self.rainfall_current or 1.0)) * 0.5)

        # Crop stress: function of temperature extremes and moisture deficit
        crop_stress = min(1.0, (
            max(0, (new_temp - 35) / 10) * 0.5 +
            max(0, (1.0 - new_humidity / 60)) * 0.3 +
            drought * 0.2
        ))

        return {
            "region_id": self.region_id,
            "region_name": self.region_name,
            "centroid_lat": self.region.get("lat", 20.0),
            "centroid_lon": self.region.get("lon", 78.0),
            "temperature_new": round(new_temp, 2),
            "rainfall_new": round(new_rainfall, 2),
            "humidity_new": round(new_humidity, 1),
            "flood_risk_new": round(flood_risk, 3),
            "drought_index_new": round(drought, 3),
            "heatwave_probability_new": round(heatwave_prob, 3),
            "crop_stress_index": round(crop_stress, 3),
        }

    def to_dict(self) -> Dict:
        return {
            "region_id": self.region_id,
            "region_name": self.region_name,
            "state_code": self.region.get("state_code"),
            "centroid_lat": self.region.get("lat"),
            "centroid_lon": self.region.get("lon"),
            "valid_at": self.last_updated.isoformat(),
            "updated_at": self.last_updated.isoformat(),
            "temperature_current": self.temperature_current,
            "rainfall_current": self.rainfall_current,
            "humidity_current": self.humidity_current,
            "lst_current": self.lst_current,
            "sst_current": self.sst_current,
            "temperature_predicted": self.temperature_predicted,
            "rainfall_predicted": self.rainfall_predicted,
            "prediction_confidence": self.prediction_confidence,
            "flood_risk": self.flood_risk,
            "heatwave_probability": self.heatwave_probability,
            "drought_index": self.drought_index,
            "temperature_anomaly": self.temperature_anomaly,
            "rainfall_anomaly": self.rainfall_anomaly,
            "data_sources": self.data_sources,
            "model_version": self.model_version,
        }


class DigitalTwinEngine:
    """
    Central Digital Twin Engine.

    Maintains ClimateState for all Indian regions and coordinates:
    - Observation ingestion
    - AI prediction application
    - Simulation scenario computation
    - State persistence
    """

    def __init__(self):
        self._states: Dict[int, ClimateState] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize twin states for all regions."""
        logger.info("Initializing Digital Twin Engine", regions=len(INDIA_STATES))
        for region in INDIA_STATES:
            self._states[region["id"]] = ClimateState(region)
        self._initialized = True
        logger.info("Digital Twin Engine initialized", states=len(self._states))

    async def update_all(self):
        """Refresh all twin states with fresh mock/real observations."""
        for region_id, state in self._states.items():
            obs = MockDataService.get_current_observation(state.region)
            state.update_with_observation(obs)

            # Simulate AI prediction
            predicted_temp = (state.temperature_current or 25.0) + random.gauss(0, 0.8)
            predicted_rainfall = max(0, (state.rainfall_current or 0.0) + random.gauss(0, 1.5))
            state.apply_prediction(
                predicted_temp=predicted_temp,
                predicted_rainfall=predicted_rainfall,
                confidence=random.uniform(0.75, 0.95),
            )

    def get_state(self, region_id: int) -> Optional[ClimateState]:
        return self._states.get(region_id)

    def get_all_states(self) -> List[Dict]:
        return [state.to_dict() for state in self._states.values()]

    def get_map_data(self) -> List[Dict]:
        """Optimized payload for GIS map rendering."""
        result = []
        for state in self._states.values():
            data = state.to_dict()
            # Determine anomaly severity
            flood = data.get("flood_risk", 0)
            heat = data.get("heatwave_probability", 0)
            if flood > 0.7 or heat > 0.7:
                severity = "emergency"
            elif flood > 0.5 or heat > 0.5:
                severity = "warning"
            elif flood > 0.3 or heat > 0.3:
                severity = "watch"
            else:
                severity = "normal"
            data["anomaly_severity"] = severity
            result.append(data)
        return result

    def run_simulation(
        self,
        temp_delta: float,
        rainfall_delta_pct: float,
        humidity_delta: float = 0.0,
        region_id: Optional[int] = None,
    ) -> List[Dict]:
        """Run a what-if simulation across all or one region."""
        targets = (
            [self._states[region_id]]
            if region_id and region_id in self._states
            else list(self._states.values())
        )

        results = []
        for state in targets:
            result = state.apply_simulation_delta(
                temp_delta=temp_delta,
                rainfall_delta_pct=rainfall_delta_pct,
                humidity_delta=humidity_delta,
            )
            results.append(result)
        return results

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Singleton instance
twin_engine = DigitalTwinEngine()
