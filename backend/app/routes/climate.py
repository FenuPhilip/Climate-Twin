"""Climate data API routes — observations, regions, time series."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.services.mock_data_service import MockDataService, INDIA_STATES
from app.services.digital_twin_engine import twin_engine

router = APIRouter()


@router.get("/regions")
async def list_regions(region_type: Optional[str] = None):
    """List all regions (states/districts)."""
    regions = MockDataService.get_regions()
    if region_type:
        regions = [r for r in regions if r.get("type", "state") == region_type]
    return {"regions": regions, "count": len(regions)}


@router.get("/regions/{region_id}")
async def get_region(region_id: int):
    """Get a single region by ID."""
    region = next((r for r in INDIA_STATES if r["id"] == region_id), None)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router.get("/current")
async def get_current_observations():
    """Get current climate observations for all regions (for map)."""
    states = twin_engine.get_all_states() if twin_engine.is_initialized else MockDataService.get_all_current_states()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "DigitalTwin",
        "data": states,
        "count": len(states),
    }


@router.get("/current/{region_id}")
async def get_current_observation_by_region(region_id: int):
    """Get current climate observation for a specific region."""
    region = next((r for r in INDIA_STATES if r["id"] == region_id), None)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    if twin_engine.is_initialized:
        state = twin_engine.get_state(region_id)
        if state:
            return state.to_dict()

    return MockDataService.get_current_observation(region)


@router.get("/timeseries/{region_id}")
async def get_time_series(
    region_id: int,
    parameter: str = Query("temperature_mean", description="Climate parameter"),
    days: int = Query(30, ge=1, le=365),
):
    """Get historical time series data for a region and parameter."""
    region = next((r for r in INDIA_STATES if r["id"] == region_id), None)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    valid_params = [
        "temperature_max", "temperature_min", "temperature_mean",
        "rainfall", "humidity", "wind_speed", "land_surface_temp",
    ]
    if parameter not in valid_params:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameter. Choose from: {valid_params}"
        )

    series = MockDataService.get_time_series(region, parameter, days=days)
    return {
        "region_id": region_id,
        "region_name": region["name"],
        "parameter": parameter,
        "unit": _get_unit(parameter),
        "days": days,
        "data": series,
    }


@router.get("/summary")
async def get_india_summary():
    """Get aggregate India-level climate summary for dashboard."""
    return MockDataService.get_india_summary()


@router.get("/map")
async def get_map_data(layer: str = Query("temperature", description="Map layer type")):
    """
    Get optimized GeoJSON-compatible climate data for map rendering.
    Layers: temperature, rainfall, flood_risk, drought_index, heatwave
    """
    valid_layers = ["temperature", "rainfall", "flood_risk", "drought_index", "heatwave_probability"]
    if layer not in valid_layers:
        raise HTTPException(status_code=400, detail=f"Invalid layer. Choose from: {valid_layers}")

    if twin_engine.is_initialized:
        data = twin_engine.get_map_data()
    else:
        data = MockDataService.get_all_current_states()

    # Build GeoJSON feature collection
    features = []
    for item in data:
        value = _get_layer_value(item, layer)
        features.append({
            "type": "Feature",
            "properties": {
                "region_id": item.get("region_id"),
                "region_name": item.get("region_name"),
                "state_code": item.get("state_code"),
                "value": value,
                "layer": layer,
                "unit": _get_unit(layer),
                "temperature": item.get("temperature_current") or item.get("temperature_mean"),
                "rainfall": item.get("rainfall_current") or item.get("rainfall"),
                "flood_risk": item.get("flood_risk", 0),
                "heatwave_probability": item.get("heatwave_probability", 0),
                "anomaly_severity": item.get("anomaly_severity", "normal"),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    item.get("centroid_lon", 78.0),
                    item.get("centroid_lat", 20.0),
                ],
            },
        })

    return {
        "type": "FeatureCollection",
        "layer": layer,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": features,
    }


@router.get("/alerts")
async def get_alerts():
    """Get active climate alerts across India."""
    import random
    alert_types = ["Heavy Rainfall", "Heatwave", "Drought Watch", "Cyclone Alert", "Flood Warning"]
    severities = ["low", "medium", "high", "extreme"]

    alerts = []
    for i, state in enumerate(INDIA_STATES[:8]):
        if random.random() > 0.5:
            alert_type = random.choice(alert_types)
            alerts.append({
                "id": i + 1,
                "region_name": state["name"],
                "region_id": state["id"],
                "alert_type": alert_type,
                "severity": random.choice(severities),
                "message": f"{alert_type} warning for {state['name']}. "
                           f"Conditions expected to persist for {random.randint(1, 5)} days.",
                "issued_at": datetime.now(timezone.utc).isoformat(),
                "is_active": True,
            })

    return {"alerts": alerts, "count": len(alerts)}


def _get_layer_value(item: dict, layer: str) -> Optional[float]:
    mapping = {
        "temperature": item.get("temperature_current") or item.get("temperature_mean"),
        "rainfall": item.get("rainfall_current") or item.get("rainfall"),
        "flood_risk": item.get("flood_risk"),
        "drought_index": item.get("drought_index"),
        "heatwave_probability": item.get("heatwave_probability"),
    }
    return mapping.get(layer)


def _get_unit(parameter: str) -> str:
    units = {
        "temperature_max": "°C",
        "temperature_min": "°C",
        "temperature_mean": "°C",
        "temperature": "°C",
        "rainfall": "mm/day",
        "humidity": "%",
        "wind_speed": "m/s",
        "land_surface_temp": "°C",
        "flood_risk": "index (0-1)",
        "drought_index": "index (0-1)",
        "heatwave_probability": "probability (0-1)",
    }
    return units.get(parameter, "")
