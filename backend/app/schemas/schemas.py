"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Auth Schemas
# ============================================================
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# ============================================================
# Region Schemas
# ============================================================
class RegionBase(BaseModel):
    name: str
    region_type: str
    state_code: Optional[str] = None
    district_code: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lon: Optional[float] = None


class RegionResponse(RegionBase):
    id: int

    class Config:
        from_attributes = True


# ============================================================
# Climate Observation Schemas
# ============================================================
class ClimateObservationResponse(BaseModel):
    id: int
    region_id: int
    source: str
    observed_at: datetime
    temperature_max: Optional[float]
    temperature_min: Optional[float]
    temperature_mean: Optional[float]
    rainfall: Optional[float]
    humidity: Optional[float]
    wind_speed: Optional[float]
    land_surface_temp: Optional[float]
    sea_surface_temp: Optional[float]
    quality_flag: int

    class Config:
        from_attributes = True


class ClimateTimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float
    quality: int = 0


class ClimateTimeSeries(BaseModel):
    region_id: int
    region_name: str
    parameter: str
    unit: str
    data: List[ClimateTimeSeriesPoint]


# ============================================================
# Digital Twin Schemas
# ============================================================
class DigitalTwinStateResponse(BaseModel):
    id: int
    region_id: int
    region_name: str
    valid_at: datetime
    updated_at: datetime

    temperature_current: Optional[float]
    rainfall_current: Optional[float]
    humidity_current: Optional[float]
    lst_current: Optional[float]
    sst_current: Optional[float]

    temperature_predicted: Optional[float]
    rainfall_predicted: Optional[float]
    prediction_confidence: Optional[float]

    temperature_anomaly: Optional[float]
    rainfall_anomaly: Optional[float]
    drought_index: Optional[float]
    flood_risk: Optional[float]
    heatwave_probability: Optional[float]

    data_sources: Optional[List[str]]
    model_version: Optional[str]

    class Config:
        from_attributes = True


class TwinMapResponse(BaseModel):
    """Optimized response for GIS map rendering."""
    region_id: int
    region_name: str
    centroid_lat: float
    centroid_lon: float
    temperature: Optional[float]
    rainfall: Optional[float]
    flood_risk: Optional[float]
    heatwave_probability: Optional[float]
    anomaly_severity: Optional[str]  # normal, watch, warning, emergency


# ============================================================
# Forecast Schemas
# ============================================================
class ForecastPoint(BaseModel):
    date: datetime
    temperature_max: Optional[float]
    temperature_min: Optional[float]
    temperature_mean: Optional[float]
    rainfall: Optional[float]
    humidity: Optional[float]
    confidence: Optional[float]
    ci_lower: Optional[float]
    ci_upper: Optional[float]


class ForecastResponse(BaseModel):
    region_id: int
    region_name: str
    generated_at: datetime
    horizon_days: int
    model_name: str
    forecasts: List[ForecastPoint]


# ============================================================
# Simulation Schemas
# ============================================================
class SimulationRequest(BaseModel):
    region_id: Optional[int] = None  # None = all India
    temperature_delta: float = Field(0.0, ge=-10, le=10, description="Temperature change in °C")
    rainfall_delta_pct: float = Field(0.0, ge=-100, le=500, description="Rainfall % change")
    humidity_delta: float = Field(0.0, ge=-50, le=50)
    wind_speed_delta: float = Field(0.0, ge=-20, le=50)
    simulation_horizon_days: int = Field(7, ge=1, le=30)
    name: Optional[str] = "Unnamed Scenario"
    description: Optional[str] = None


class SimulationResultRegion(BaseModel):
    region_id: int
    region_name: str
    centroid_lat: float
    centroid_lon: float
    temperature_new: float
    rainfall_new: float
    flood_risk_new: float
    drought_index_new: float
    crop_stress_index: float
    heatwave_probability_new: float


class SimulationResponse(BaseModel):
    scenario_id: int
    name: str
    status: str
    parameters: SimulationRequest
    results: List[SimulationResultRegion]
    summary: Dict[str, Any]
    generated_at: datetime


# ============================================================
# Analytics Schemas
# ============================================================
class ModelPerformanceMetrics(BaseModel):
    model_name: str
    target_variable: str
    mae: float
    rmse: float
    r2_score: float
    evaluation_period: str
    sample_count: int


class AnalyticsSummary(BaseModel):
    total_regions: int
    data_coverage_pct: float
    active_alerts: int
    models_active: int
    last_update: datetime
    data_sources: List[str]


class HistoricalComparison(BaseModel):
    region_name: str
    parameter: str
    period_a: str
    period_b: str
    mean_a: float
    mean_b: float
    delta: float
    delta_pct: float
    trend: str  # increasing, decreasing, stable


# ============================================================
# Dashboard Schemas
# ============================================================
class DashboardOverview(BaseModel):
    timestamp: datetime
    india_avg_temperature: float
    india_avg_rainfall: float
    active_alerts: int
    regions_monitored: int
    predictions_made_today: int
    data_freshness_minutes: int
    recent_alerts: List[Dict[str, Any]]
    top_anomalies: List[Dict[str, Any]]


# ============================================================
# AI Assistant Schemas
# ============================================================
class AssistantMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: datetime


class AssistantRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class AssistantResponse(BaseModel):
    response: str
    session_id: str
    sources: List[str] = []
    confidence: float = 0.8
    suggested_actions: List[str] = []
