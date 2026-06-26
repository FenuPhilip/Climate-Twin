"""
SQLAlchemy ORM Models for ClimateTwin India.

All geospatial columns use GeoAlchemy2 (PostGIS).
"""
from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# ============================================================
# Users
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="researcher")  # admin, researcher, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================
# Regions (India administrative boundaries)
# ============================================================
class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    region_type = Column(String(50), nullable=False)  # country, state, district
    state_code = Column(String(10), index=True)
    district_code = Column(String(20), index=True)
    parent_id = Column(Integer, ForeignKey("regions.id"), nullable=True)

    # PostGIS geometry
    geometry = Column(Geometry("MULTIPOLYGON", srid=4326))
    centroid_lat = Column(Float)
    centroid_lon = Column(Float)

    # Relationships
    parent = relationship("Region", remote_side=[id], backref="children")
    observations = relationship("ClimateObservation", back_populates="region")
    twin_states = relationship("DigitalTwinState", back_populates="region")

    __table_args__ = (
        Index("idx_regions_geometry", "geometry", postgresql_using="gist"),
    )


# ============================================================
# Climate Observations (raw ingested data)
# ============================================================
class ClimateObservation(Base):
    __tablename__ = "climate_observations"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)  # IMD, INSAT, MOSDAC
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    # Meteorological parameters
    temperature_max = Column(Float)       # °C
    temperature_min = Column(Float)       # °C
    temperature_mean = Column(Float)      # °C
    rainfall = Column(Float)             # mm
    humidity = Column(Float)             # %
    wind_speed = Column(Float)           # m/s
    wind_direction = Column(Float)       # degrees
    pressure = Column(Float)             # hPa

    # Satellite-derived parameters
    land_surface_temp = Column(Float)    # °C (INSAT LST)
    sea_surface_temp = Column(Float)     # °C (INSAT SST)
    cloud_cover = Column(Float)         # %
    ndvi = Column(Float)                # Normalized Difference Vegetation Index

    # Quality
    quality_flag = Column(Integer, default=0)  # 0=good, 1=suspect, 2=bad
    raw_metadata = Column(JSON)

    # Relationships
    region = relationship("Region", back_populates="observations")

    __table_args__ = (
        Index("idx_obs_region_time", "region_id", "observed_at"),
        Index("idx_obs_source_time", "source", "observed_at"),
    )


# ============================================================
# Digital Twin State (current virtual climate model)
# ============================================================
class DigitalTwinState(Base):
    __tablename__ = "digital_twin_states"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    valid_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Current observed state
    temperature_current = Column(Float)
    rainfall_current = Column(Float)
    humidity_current = Column(Float)
    lst_current = Column(Float)
    sst_current = Column(Float)

    # AI-predicted state
    temperature_predicted = Column(Float)
    rainfall_predicted = Column(Float)
    prediction_confidence = Column(Float)   # 0–1
    prediction_horizon_hours = Column(Integer, default=24)

    # Anomaly indicators
    temperature_anomaly = Column(Float)     # deviation from climatological mean
    rainfall_anomaly = Column(Float)
    drought_index = Column(Float)
    flood_risk = Column(Float)              # 0–1
    heatwave_probability = Column(Float)   # 0–1

    # Data source metadata
    data_sources = Column(JSON)             # list of sources contributing
    model_version = Column(String(50))

    region = relationship("Region", back_populates="twin_states")

    __table_args__ = (
        Index("idx_twin_region_valid", "region_id", "valid_at"),
    )


# ============================================================
# Climate Forecasts
# ============================================================
class ClimateForecast(Base):
    __tablename__ = "climate_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, index=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    forecast_for = Column(DateTime(timezone=True), nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False)

    # Forecast values
    temperature_max = Column(Float)
    temperature_min = Column(Float)
    temperature_mean = Column(Float)
    rainfall = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)

    # Uncertainty
    temperature_uncertainty = Column(Float)
    rainfall_uncertainty = Column(Float)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)

    # Model info
    model_name = Column(String(100))
    model_version = Column(String(50))
    prediction_metrics = Column(JSON)

    region = relationship("Region")

    __table_args__ = (
        Index("idx_forecast_region_horizon", "region_id", "forecast_for"),
    )


# ============================================================
# Simulation Scenarios
# ============================================================
class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(255))
    description = Column(Text)

    # Input parameters
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    temperature_delta = Column(Float, default=0.0)    # °C change
    rainfall_delta_pct = Column(Float, default=0.0)   # % change
    humidity_delta = Column(Float, default=0.0)
    wind_speed_delta = Column(Float, default=0.0)
    simulation_horizon_days = Column(Integer, default=7)

    # Results
    status = Column(String(50), default="pending")   # pending, running, completed, failed
    results = Column(JSON)
    completed_at = Column(DateTime(timezone=True))

    user = relationship("User")
    region = relationship("Region")


# ============================================================
# Model Registry
# ============================================================
class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    model_type = Column(String(100))     # lstm, random_forest, xgboost, gru
    target_variable = Column(String(100))  # rainfall, temperature_max, temperature_min
    version = Column(String(50))
    trained_at = Column(DateTime(timezone=True))
    file_path = Column(String(500))

    # Performance metrics
    mae = Column(Float)
    rmse = Column(Float)
    r2_score = Column(Float)
    training_loss = Column(Float)
    validation_loss = Column(Float)

    is_active = Column(Boolean, default=False)
    metadata = Column(JSON)


# ============================================================
# Dataset Ingestion Log
# ============================================================
class DataIngestionLog(Base):
    __tablename__ = "data_ingestion_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)
    dataset_type = Column(String(100))
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    records_count = Column(Integer)
    status = Column(String(50))   # success, partial, failed
    error_message = Column(Text)
    file_path = Column(String(500))
    metadata = Column(JSON)


# ============================================================
# Climate Alerts
# ============================================================
class ClimateAlert(Base):
    __tablename__ = "climate_alerts"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, index=True)
    alert_type = Column(String(100))   # heatwave, heavy_rainfall, drought, flood
    severity = Column(String(50))     # low, medium, high, extreme
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    message = Column(Text)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)

    region = relationship("Region")
