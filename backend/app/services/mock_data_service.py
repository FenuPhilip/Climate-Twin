"""
Mock Data Service — Generates realistic synthetic climate data for India.

All mock data is scientifically calibrated to match India's climate patterns:
- Monsoon seasonality (June–September)
- Regional temperature ranges
- State-level rainfall distributions
"""
import random
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any


# India states with realistic climate parameters
INDIA_STATES = [
    {"id": 1, "name": "Andhra Pradesh", "state_code": "AP", "lat": 15.9129, "lon": 79.7400, "climate": "tropical"},
    {"id": 2, "name": "Arunachal Pradesh", "state_code": "AR", "lat": 28.2180, "lon": 94.7278, "climate": "subtropical"},
    {"id": 3, "name": "Assam", "state_code": "AS", "lat": 26.2006, "lon": 92.9376, "climate": "tropical_wet"},
    {"id": 4, "name": "Bihar", "state_code": "BR", "lat": 25.0961, "lon": 85.3131, "climate": "humid_subtropical"},
    {"id": 5, "name": "Chhattisgarh", "state_code": "CG", "lat": 21.2787, "lon": 81.8661, "climate": "tropical"},
    {"id": 6, "name": "Goa", "state_code": "GA", "lat": 15.2993, "lon": 74.1240, "climate": "tropical_wet"},
    {"id": 7, "name": "Gujarat", "state_code": "GJ", "lat": 22.2587, "lon": 71.1924, "climate": "semi_arid"},
    {"id": 8, "name": "Haryana", "state_code": "HR", "lat": 29.0588, "lon": 76.0856, "climate": "semi_arid"},
    {"id": 9, "name": "Himachal Pradesh", "state_code": "HP", "lat": 31.1048, "lon": 77.1734, "climate": "alpine"},
    {"id": 10, "name": "Jharkhand", "state_code": "JH", "lat": 23.6102, "lon": 85.2799, "climate": "humid_subtropical"},
    {"id": 11, "name": "Karnataka", "state_code": "KA", "lat": 15.3173, "lon": 75.7139, "climate": "tropical"},
    {"id": 12, "name": "Kerala", "state_code": "KL", "lat": 10.8505, "lon": 76.2711, "climate": "tropical_wet"},
    {"id": 13, "name": "Madhya Pradesh", "state_code": "MP", "lat": 22.9734, "lon": 78.6569, "climate": "tropical"},
    {"id": 14, "name": "Maharashtra", "state_code": "MH", "lat": 19.7515, "lon": 75.7139, "climate": "tropical"},
    {"id": 15, "name": "Manipur", "state_code": "MN", "lat": 24.6637, "lon": 93.9063, "climate": "subtropical"},
    {"id": 16, "name": "Meghalaya", "state_code": "ML", "lat": 25.4670, "lon": 91.3662, "climate": "tropical_wet"},
    {"id": 17, "name": "Mizoram", "state_code": "MZ", "lat": 23.1645, "lon": 92.9376, "climate": "subtropical"},
    {"id": 18, "name": "Nagaland", "state_code": "NL", "lat": 26.1584, "lon": 94.5624, "climate": "subtropical"},
    {"id": 19, "name": "Odisha", "state_code": "OD", "lat": 20.9517, "lon": 85.0985, "climate": "tropical"},
    {"id": 20, "name": "Punjab", "state_code": "PB", "lat": 31.1471, "lon": 75.3412, "climate": "semi_arid"},
    {"id": 21, "name": "Rajasthan", "state_code": "RJ", "lat": 27.0238, "lon": 74.2179, "climate": "arid"},
    {"id": 22, "name": "Sikkim", "state_code": "SK", "lat": 27.5330, "lon": 88.5122, "climate": "alpine"},
    {"id": 23, "name": "Tamil Nadu", "state_code": "TN", "lat": 11.1271, "lon": 78.6569, "climate": "tropical"},
    {"id": 24, "name": "Telangana", "state_code": "TS", "lat": 18.1124, "lon": 79.0193, "climate": "tropical"},
    {"id": 25, "name": "Tripura", "state_code": "TR", "lat": 23.9408, "lon": 91.9882, "climate": "tropical_wet"},
    {"id": 26, "name": "Uttar Pradesh", "state_code": "UP", "lat": 26.8467, "lon": 80.9462, "climate": "humid_subtropical"},
    {"id": 27, "name": "Uttarakhand", "state_code": "UK", "lat": 30.0668, "lon": 79.0193, "climate": "alpine"},
    {"id": 28, "name": "West Bengal", "state_code": "WB", "lat": 22.9868, "lon": 87.8550, "climate": "tropical_wet"},
    {"id": 29, "name": "Delhi", "state_code": "DL", "lat": 28.7041, "lon": 77.1025, "climate": "semi_arid"},
    {"id": 30, "name": "Jammu & Kashmir", "state_code": "JK", "lat": 33.7782, "lon": 76.5762, "climate": "alpine"},
]

# Climate parameter ranges by type
CLIMATE_PROFILES = {
    "tropical_wet": {"temp_mean": 27, "temp_range": 5, "rainfall_mean": 8, "rainfall_std": 6},
    "tropical": {"temp_mean": 28, "temp_range": 8, "rainfall_mean": 4, "rainfall_std": 4},
    "humid_subtropical": {"temp_mean": 24, "temp_range": 10, "rainfall_mean": 3, "rainfall_std": 3},
    "semi_arid": {"temp_mean": 25, "temp_range": 12, "rainfall_mean": 1.5, "rainfall_std": 2},
    "arid": {"temp_mean": 28, "temp_range": 15, "rainfall_mean": 0.5, "rainfall_std": 1},
    "alpine": {"temp_mean": 10, "temp_range": 10, "rainfall_mean": 2, "rainfall_std": 2},
    "subtropical": {"temp_mean": 22, "temp_range": 8, "rainfall_mean": 5, "rainfall_std": 4},
}


def _monsoon_factor(month: int) -> float:
    """Returns a multiplier for monsoon season (June–Sept)."""
    if 6 <= month <= 9:
        peak = 8  # August peak
        return 1.0 + 2.5 * math.exp(-0.5 * ((month - peak) / 1.5) ** 2)
    elif month in [5, 10]:
        return 0.6
    return 0.15


def _get_noise(scale: float = 1.0) -> float:
    return random.gauss(0, scale)


class MockDataService:
    """Generates realistic synthetic climate observations for all Indian states."""

    @staticmethod
    def get_regions() -> List[Dict]:
        return INDIA_STATES

    @staticmethod
    def get_current_observation(region: Dict, timestamp: Optional[datetime] = None) -> Dict:
        """Generate a realistic current climate observation for a region."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        month = timestamp.month
        day_of_year = timestamp.timetuple().tm_yday
        hour = timestamp.hour

        profile = CLIMATE_PROFILES.get(region["climate"], CLIMATE_PROFILES["tropical"])
        monsoon = _monsoon_factor(month)

        # Temperature with diurnal cycle
        base_temp = profile["temp_mean"] + profile["temp_range"] * math.sin(
            math.pi * (day_of_year - 80) / 183
        )
        diurnal = profile["temp_range"] * 0.3 * math.sin(math.pi * (hour - 6) / 12)
        temp_mean = base_temp + diurnal + _get_noise(1.5)

        temp_max = temp_mean + random.uniform(3, 7)
        temp_min = temp_mean - random.uniform(3, 7)

        # Rainfall
        rainfall_base = profile["rainfall_mean"] * monsoon
        rainfall = max(0, random.gauss(rainfall_base, profile["rainfall_std"]))

        # Humidity (inversely correlated with aridity, positively with rainfall)
        humidity_base = 60 + monsoon * 20 - (profile["temp_mean"] - 20)
        humidity = min(100, max(20, humidity_base + _get_noise(8)))

        # LST slightly higher than air temperature
        lst = temp_mean + random.uniform(1, 5)

        # SST for coastal states
        coastal_states = {"AP", "GJ", "GJ", "KA", "KL", "MH", "OD", "TN", "WB", "GJ"}
        sst = None
        if region["state_code"] in coastal_states:
            sst = 27 + _get_noise(1.5) + monsoon * 0.5

        wind_speed = random.uniform(1, 8) * (1 + monsoon * 0.3)

        # Derived risk indices
        flood_risk = min(1.0, rainfall / 20.0 * monsoon * 0.5) if rainfall > 5 else 0.0
        heatwave_prob = max(0.0, (temp_max - 40) / 10) if month in [4, 5, 6] else 0.0
        drought_index = max(0.0, 1 - (rainfall / profile["rainfall_mean"]) * 0.5) if profile["rainfall_mean"] > 0 else 0.5

        return {
            "region_id": region["id"],
            "region_name": region["name"],
            "state_code": region["state_code"],
            "centroid_lat": region["lat"],
            "centroid_lon": region["lon"],
            "observed_at": timestamp.isoformat(),
            "source": "IMD_MOCK",
            "temperature_max": round(temp_max, 2),
            "temperature_min": round(temp_min, 2),
            "temperature_mean": round(temp_mean, 2),
            "rainfall": round(rainfall, 2),
            "humidity": round(humidity, 1),
            "wind_speed": round(wind_speed, 1),
            "land_surface_temp": round(lst, 2),
            "sea_surface_temp": round(sst, 2) if sst else None,
            "flood_risk": round(flood_risk, 3),
            "heatwave_probability": round(heatwave_prob, 3),
            "drought_index": round(drought_index, 3),
            "temperature_anomaly": round(_get_noise(1.2), 2),
            "rainfall_anomaly": round(_get_noise(2.0), 2),
        }

    @staticmethod
    def get_time_series(
        region: Dict,
        parameter: str,
        days: int = 30,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Generate historical time series data."""
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        series = []
        for i in range(days, -1, -1):
            ts = end_date - timedelta(days=i)
            obs = MockDataService.get_current_observation(region, ts)
            series.append({
                "timestamp": ts.isoformat(),
                "value": obs.get(parameter, 0.0),
                "quality": 0,
            })
        return series

    @staticmethod
    def get_forecast(region: Dict, horizon_days: int = 7) -> List[Dict]:
        """Generate AI forecast for a region."""
        now = datetime.now(timezone.utc)
        forecasts = []

        for i in range(1, horizon_days + 1):
            future_ts = now + timedelta(days=i)
            obs = MockDataService.get_current_observation(region, future_ts)
            # Add uncertainty that grows with horizon
            uncertainty = 0.1 + (i * 0.05)
            forecasts.append({
                "date": future_ts.isoformat(),
                "temperature_max": obs["temperature_max"],
                "temperature_min": obs["temperature_min"],
                "temperature_mean": obs["temperature_mean"],
                "rainfall": obs["rainfall"],
                "humidity": obs["humidity"],
                "confidence": round(max(0.4, 0.95 - uncertainty), 3),
                "ci_lower": round(obs["temperature_mean"] - uncertainty * 5, 2),
                "ci_upper": round(obs["temperature_mean"] + uncertainty * 5, 2),
            })
        return forecasts

    @staticmethod
    def get_all_current_states() -> List[Dict]:
        """Get current climate state for all regions (for map)."""
        return [
            MockDataService.get_current_observation(region)
            for region in INDIA_STATES
        ]

    @staticmethod
    def get_india_summary() -> Dict:
        """Get aggregate India-level climate summary."""
        states = MockDataService.get_all_current_states()
        temps = [s["temperature_mean"] for s in states]
        rainfalls = [s["rainfall"] for s in states]
        now = datetime.now(timezone.utc)

        return {
            "timestamp": now.isoformat(),
            "india_avg_temperature": round(sum(temps) / len(temps), 2),
            "india_avg_rainfall": round(sum(rainfalls) / len(rainfalls), 2),
            "india_max_temperature": round(max(temps), 2),
            "india_min_temperature": round(min(temps), 2),
            "total_regions_monitored": len(states),
            "active_alerts": random.randint(2, 8),
            "predictions_made_today": random.randint(150, 300),
            "data_freshness_minutes": random.randint(5, 30),
            "hottest_state": max(states, key=lambda s: s["temperature_max"])["region_name"],
            "wettest_state": max(states, key=lambda s: s["rainfall"])["region_name"],
        }
