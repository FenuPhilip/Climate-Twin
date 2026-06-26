"""Datasets API routes — dataset catalog and download info."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog")
async def list_datasets():
    return {
        "datasets": [
            {
                "id": "imd_rainfall_daily",
                "name": "IMD Daily Rainfall (1901–2023)",
                "source": "India Meteorological Department",
                "format": "NetCDF / CSV",
                "resolution": "0.25° × 0.25°",
                "temporal_coverage": "1901–2023",
                "parameters": ["rainfall"],
                "status": "available_mock",
                "url": "https://imdpune.gov.in/",
            },
            {
                "id": "imd_temperature_daily",
                "name": "IMD Daily Temperature (1951–2023)",
                "source": "India Meteorological Department",
                "format": "NetCDF / CSV",
                "resolution": "1° × 1°",
                "temporal_coverage": "1951–2023",
                "parameters": ["temperature_max", "temperature_min"],
                "status": "available_mock",
                "url": "https://imdpune.gov.in/",
            },
            {
                "id": "insat_lst",
                "name": "INSAT-3D Land Surface Temperature",
                "source": "ISRO / MOSDAC",
                "format": "HDF5",
                "resolution": "4 km",
                "temporal_coverage": "2013–present",
                "parameters": ["land_surface_temp"],
                "status": "interface_ready",
                "url": "https://mosdac.gov.in/",
            },
            {
                "id": "insat_sst",
                "name": "INSAT-3D Sea Surface Temperature",
                "source": "ISRO / MOSDAC",
                "format": "HDF5",
                "resolution": "4 km",
                "temporal_coverage": "2013–present",
                "parameters": ["sea_surface_temp"],
                "status": "interface_ready",
                "url": "https://mosdac.gov.in/",
            },
            {
                "id": "insat_rainfall",
                "name": "INSAT-3D Precipitation",
                "source": "ISRO / MOSDAC",
                "format": "HDF5",
                "resolution": "4 km",
                "temporal_coverage": "2013–present",
                "parameters": ["rainfall"],
                "status": "interface_ready",
                "url": "https://mosdac.gov.in/",
            },
        ]
    }
