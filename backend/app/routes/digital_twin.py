"""Digital Twin API routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.services.digital_twin_engine import twin_engine
from app.services.mock_data_service import INDIA_STATES

router = APIRouter()


@router.get("/status")
async def twin_status():
    return {
        "initialized": twin_engine.is_initialized,
        "regions_tracked": len(INDIA_STATES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_version": "mock-v1.0",
    }


@router.get("/states")
async def get_all_twin_states():
    """Get current Digital Twin state for all regions."""
    if not twin_engine.is_initialized:
        raise HTTPException(status_code=503, detail="Digital Twin not yet initialized")
    return {
        "states": twin_engine.get_all_states(),
        "count": len(INDIA_STATES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/states/{region_id}")
async def get_twin_state(region_id: int):
    """Get Digital Twin state for a specific region."""
    if not twin_engine.is_initialized:
        raise HTTPException(status_code=503, detail="Digital Twin not yet initialized")
    state = twin_engine.get_state(region_id)
    if not state:
        raise HTTPException(status_code=404, detail="Region not found in Digital Twin")
    return state.to_dict()


@router.post("/refresh")
async def refresh_twin():
    """Trigger immediate Digital Twin update."""
    await twin_engine.update_all()
    return {
        "status": "refreshed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regions_updated": len(INDIA_STATES),
    }


@router.get("/map")
async def get_twin_map():
    """Get optimized twin state for GIS map rendering."""
    if not twin_engine.is_initialized:
        from app.services.mock_data_service import MockDataService
        return {"features": MockDataService.get_all_current_states()}
    return {"features": twin_engine.get_map_data()}
