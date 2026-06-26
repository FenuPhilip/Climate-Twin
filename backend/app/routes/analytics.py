"""Analytics API routes — trends, model performance, historical comparisons."""
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Query

from app.services.mock_data_service import MockDataService, INDIA_STATES

router = APIRouter()


@router.get("/model-performance")
async def get_model_performance():
    """Get AI model evaluation metrics."""
    return {
        "models": [
            {
                "model_name": "ClimateTwin-LSTM",
                "target_variable": "rainfall",
                "mae": round(random.uniform(1.2, 2.5), 3),
                "rmse": round(random.uniform(2.1, 4.0), 3),
                "r2_score": round(random.uniform(0.82, 0.94), 3),
                "evaluation_period": "Jan 2024 – Jun 2024",
                "sample_count": 18250,
                "architecture": "LSTM (128 units, 2 layers)",
                "training_data": "IMD Daily Rainfall 1990–2023",
            },
            {
                "model_name": "ClimateTwin-LSTM",
                "target_variable": "temperature_max",
                "mae": round(random.uniform(0.8, 1.5), 3),
                "rmse": round(random.uniform(1.2, 2.0), 3),
                "r2_score": round(random.uniform(0.88, 0.96), 3),
                "evaluation_period": "Jan 2024 – Jun 2024",
                "sample_count": 18250,
                "architecture": "LSTM (128 units, 2 layers)",
                "training_data": "IMD Temperature 1990–2023",
            },
            {
                "model_name": "RandomForest-Baseline",
                "target_variable": "rainfall",
                "mae": round(random.uniform(2.0, 3.5), 3),
                "rmse": round(random.uniform(3.5, 5.5), 3),
                "r2_score": round(random.uniform(0.70, 0.82), 3),
                "evaluation_period": "Jan 2024 – Jun 2024",
                "sample_count": 18250,
                "architecture": "Random Forest (200 trees)",
                "training_data": "IMD Daily Rainfall 1990–2023",
            },
        ]
    }


@router.get("/trends/{region_id}")
async def get_climate_trends(
    region_id: int,
    parameter: str = Query("temperature_mean"),
    years: int = Query(10, ge=1, le=30),
):
    """Get multi-year climate trend for a region."""
    region = next((r for r in INDIA_STATES if r["id"] == region_id), None)
    if not region:
        from fastapi import HTTPException
        raise HTTPException(404, "Region not found")

    now = datetime.now(timezone.utc)
    trend_data = []

    for y in range(years, -1, -1):
        year = now.year - y
        # Generate yearly aggregates
        monthly = []
        for m in range(1, 13):
            ts = datetime(year, m, 15, tzinfo=timezone.utc)
            obs = MockDataService.get_current_observation(region, ts)
            monthly.append(obs.get(parameter, 0.0))

        annual_avg = sum(monthly) / len(monthly)
        trend_data.append({
            "year": year,
            "annual_mean": round(annual_avg, 2),
            "monthly": [round(v, 2) for v in monthly],
        })

    # Calculate trend slope
    values = [d["annual_mean"] for d in trend_data]
    n = len(values)
    slope = (values[-1] - values[0]) / max(n - 1, 1)

    return {
        "region_id": region_id,
        "region_name": region["name"],
        "parameter": parameter,
        "years": years,
        "trend_slope_per_year": round(slope, 4),
        "trend_direction": "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "stable",
        "data": trend_data,
    }


@router.get("/comparison")
async def compare_regions(
    region_a_id: int = Query(...),
    region_b_id: int = Query(...),
    parameter: str = Query("temperature_mean"),
    days: int = Query(30),
):
    """Compare climate data between two regions."""
    region_a = next((r for r in INDIA_STATES if r["id"] == region_a_id), None)
    region_b = next((r for r in INDIA_STATES if r["id"] == region_b_id), None)

    if not region_a or not region_b:
        from fastapi import HTTPException
        raise HTTPException(404, "One or both regions not found")

    series_a = MockDataService.get_time_series(region_a, parameter, days=days)
    series_b = MockDataService.get_time_series(region_b, parameter, days=days)

    avg_a = sum(p["value"] for p in series_a) / len(series_a) if series_a else 0
    avg_b = sum(p["value"] for p in series_b) / len(series_b) if series_b else 0

    return {
        "parameter": parameter,
        "days": days,
        "region_a": {
            "id": region_a_id,
            "name": region_a["name"],
            "mean": round(avg_a, 2),
            "series": series_a,
        },
        "region_b": {
            "id": region_b_id,
            "name": region_b["name"],
            "mean": round(avg_b, 2),
            "series": series_b,
        },
        "delta": round(avg_a - avg_b, 2),
        "delta_pct": round(((avg_a - avg_b) / max(abs(avg_b), 0.001)) * 100, 1),
    }


@router.get("/summary")
async def get_analytics_summary():
    """Get overall analytics summary."""
    summary = MockDataService.get_india_summary()
    return {
        **summary,
        "models_active": 4,
        "model_accuracy_rainfall": round(random.uniform(0.82, 0.94) * 100, 1),
        "model_accuracy_temperature": round(random.uniform(0.88, 0.96) * 100, 1),
        "data_sources": ["IMD", "INSAT-3D", "INSAT-3DR", "MOSDAC", "Cartosat-2"],
        "total_observations_processed": random.randint(500000, 1000000),
        "coverage_pct": 98.7,
    }


@router.get("/heatmap-data")
async def get_heatmap_data(
    parameter: str = Query("rainfall"),
    month: int = Query(datetime.now().month, ge=1, le=12),
):
    """Get monthly heatmap data for all regions."""
    now = datetime.now(timezone.utc).replace(month=month, day=15)
    data = []
    for region in INDIA_STATES:
        obs = MockDataService.get_current_observation(region, now)
        data.append({
            "region_id": region["id"],
            "region_name": region["name"],
            "lat": region["lat"],
            "lon": region["lon"],
            "value": obs.get(parameter, 0),
        })
    return {"month": month, "parameter": parameter, "data": data}
