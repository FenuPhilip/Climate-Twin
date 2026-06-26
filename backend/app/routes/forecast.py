"""Forecast API routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query

from app.services.mock_data_service import MockDataService, INDIA_STATES

router = APIRouter()


@router.get("/{region_id}")
async def get_forecast(
    region_id: int,
    horizon_days: int = Query(7, ge=1, le=14, description="Forecast horizon in days"),
):
    """Get AI-generated climate forecast for a region."""
    region = next((r for r in INDIA_STATES if r["id"] == region_id), None)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    forecasts = MockDataService.get_forecast(region, horizon_days=horizon_days)

    return {
        "region_id": region_id,
        "region_name": region["name"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "horizon_days": horizon_days,
        "model_name": "ClimateTwin-LSTM-v1.0",
        "model_description": "Long Short-Term Memory neural network trained on 30 years of IMD data",
        "forecasts": forecasts,
    }


@router.get("/")
async def get_all_forecasts(horizon_days: int = Query(7, ge=1, le=14)):
    """Get forecasts for all regions."""
    forecasts = {}
    for region in INDIA_STATES:
        forecasts[region["id"]] = {
            "region_name": region["name"],
            "forecast": MockDataService.get_forecast(region, horizon_days=horizon_days),
        }
    return {
        "horizon_days": horizon_days,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regions": forecasts,
    }
