"""Simulation (What-if) API routes."""
import random
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Body

from app.schemas.schemas import SimulationRequest, SimulationResponse
from app.services.digital_twin_engine import twin_engine

router = APIRouter()


@router.post("/run", response_model=SimulationResponse)
async def run_simulation(req: SimulationRequest):
    """
    Run a what-if climate simulation.
    
    Apply parameter deltas across all or a specific region and compute cascading effects:
    - New temperature, rainfall
    - Updated flood risk, drought index
    - Crop stress index
    - Heatwave probability
    """
    if not twin_engine.is_initialized:
        raise HTTPException(status_code=503, detail="Digital Twin not yet initialized")

    results = twin_engine.run_simulation(
        temp_delta=req.temperature_delta,
        rainfall_delta_pct=req.rainfall_delta_pct,
        humidity_delta=req.humidity_delta,
        region_id=req.region_id,
    )

    # Compute summary statistics
    avg_flood_risk = sum(r["flood_risk_new"] for r in results) / len(results) if results else 0
    avg_drought = sum(r["drought_index_new"] for r in results) / len(results) if results else 0
    max_heatwave = max((r["heatwave_probability_new"] for r in results), default=0)
    avg_temp = sum(r["temperature_new"] for r in results) / len(results) if results else 0

    # Determine risk alerts from simulation
    risk_alerts = []
    if avg_flood_risk > 0.5:
        risk_alerts.append(f"HIGH FLOOD RISK: {avg_flood_risk:.0%} regions exceed threshold")
    if max_heatwave > 0.6:
        risk_alerts.append(f"HEATWAVE WARNING: Peak probability {max_heatwave:.0%}")
    if avg_drought > 0.6:
        risk_alerts.append(f"DROUGHT ALERT: Average drought index {avg_drought:.2f}")

    scenario_id = random.randint(1000, 9999)

    return SimulationResponse(
        scenario_id=scenario_id,
        name=req.name or "What-if Scenario",
        status="completed",
        parameters=req,
        results=results,
        summary={
            "regions_affected": len(results),
            "avg_temperature": round(avg_temp, 2),
            "avg_flood_risk": round(avg_flood_risk, 3),
            "avg_drought_index": round(avg_drought, 3),
            "max_heatwave_probability": round(max_heatwave, 3),
            "risk_alerts": risk_alerts,
            "simulation_horizon_days": req.simulation_horizon_days,
        },
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/presets")
async def get_simulation_presets():
    """Return predefined simulation scenarios for quick use."""
    return {
        "presets": [
            {
                "id": "moderate_warming",
                "name": "Moderate Warming (+2°C)",
                "description": "Simulate 2°C temperature increase — IPCC RCP4.5 scenario",
                "params": {"temperature_delta": 2.0, "rainfall_delta_pct": -5.0},
            },
            {
                "id": "extreme_warming",
                "name": "Extreme Warming (+4°C)",
                "description": "Simulate 4°C temperature increase — IPCC RCP8.5 scenario",
                "params": {"temperature_delta": 4.0, "rainfall_delta_pct": -15.0},
            },
            {
                "id": "extreme_rainfall",
                "name": "Extreme Monsoon (+50% Rainfall)",
                "description": "Simulate enhanced monsoon — flood risk assessment",
                "params": {"temperature_delta": 0.5, "rainfall_delta_pct": 50.0},
            },
            {
                "id": "drought",
                "name": "Drought Scenario (-60% Rainfall)",
                "description": "Simulate severe drought conditions",
                "params": {"temperature_delta": 1.5, "rainfall_delta_pct": -60.0},
            },
            {
                "id": "heatwave",
                "name": "Heatwave Event (+5°C, -30% Humidity)",
                "description": "Simulate extreme heat event",
                "params": {"temperature_delta": 5.0, "rainfall_delta_pct": -30.0, "humidity_delta": -30.0},
            },
        ]
    }
