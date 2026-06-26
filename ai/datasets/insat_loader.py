"""
INSAT / MOSDAC Dataset Loader

Handles:
- INSAT-3D Land Surface Temperature (LST)
- INSAT-3D Sea Surface Temperature (SST)
- INSAT-3D Precipitation
- MOSDAC satellite products

Real data format: HDF5 (.h5) or NetCDF (.nc)
PLUG-IN POINT: Replace mock methods with real HDF5/NetCDF parsing
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class INSATDataLoader:
    """
    Loads INSAT-3D / MOSDAC satellite products.

    Supports:
    - Mock data (default)
    - HDF5 files from MOSDAC (plug-in point)
    - NetCDF from ISRO data archive (plug-in point)
    """

    def __init__(
        self,
        source: str = "mock",
        data_path: Optional[Path] = None,
        mosdac_token: Optional[str] = None,
    ):
        self.source = source
        self.data_path = data_path
        self.mosdac_token = mosdac_token
        logger.info(f"INSATDataLoader initialized with source={source}")

    def load_lst(
        self,
        lat_min: float = 8.0,
        lat_max: float = 37.0,
        lon_min: float = 68.0,
        lon_max: float = 97.5,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Load Land Surface Temperature data."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        if self.source == "mock":
            return self._generate_mock_lst(lat_min, lat_max, lon_min, lon_max, start_date, end_date)
        elif self.source == "hdf5":
            return self._load_hdf5_lst(start_date, end_date)
        else:
            return self._generate_mock_lst(lat_min, lat_max, lon_min, lon_max, start_date, end_date)

    def load_sst(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Load Sea Surface Temperature data."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        if self.source == "mock":
            return self._generate_mock_sst(start_date, end_date)
        elif self.source == "hdf5":
            return self._load_hdf5_sst(start_date, end_date)
        else:
            return self._generate_mock_sst(start_date, end_date)

    def load_precipitation(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Load INSAT satellite precipitation estimates."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        return self._generate_mock_precipitation(start_date, end_date)

    def _generate_mock_lst(
        self, lat_min, lat_max, lon_min, lon_max, start, end
    ) -> pd.DataFrame:
        """Generate mock gridded LST data."""
        dates = pd.date_range(start=start, end=end, freq="3H")
        lats = np.arange(lat_min, lat_max, 2.0)
        lons = np.arange(lon_min, lon_max, 2.0)

        records = []
        for date in dates[:100]:  # limit to 100 timesteps
            for lat in lats[:5]:  # 5 lat points for performance
                for lon in lons[:5]:
                    base_temp = 25 + (lat - 20) * 0.3 + np.random.normal(0, 2)
                    diurnal = 5 * np.sin(np.pi * (date.hour - 6) / 12)
                    lst = base_temp + diurnal
                    records.append({
                        "timestamp": date,
                        "lat": round(lat, 2),
                        "lon": round(lon, 2),
                        "lst_celsius": round(lst, 2),
                        "quality": 0,
                        "source": "INSAT-3D_MOCK",
                    })

        return pd.DataFrame(records)

    def _generate_mock_sst(self, start: datetime, end: datetime) -> pd.DataFrame:
        """Generate mock SST data for Indian Ocean / Arabian Sea / Bay of Bengal."""
        dates = pd.date_range(start=start, end=end, freq="D")

        # Indian Ocean SST grid points
        sea_points = [
            {"name": "Arabian Sea", "lat": 15.0, "lon": 65.0, "base_sst": 27.5},
            {"name": "Bay of Bengal", "lat": 12.0, "lon": 86.0, "base_sst": 28.0},
            {"name": "Indian Ocean South", "lat": 5.0, "lon": 75.0, "base_sst": 28.5},
        ]

        records = []
        for date in dates:
            for point in sea_points:
                seasonal = 1.5 * np.sin(np.pi * (date.month - 4) / 6)
                sst = point["base_sst"] + seasonal + np.random.normal(0, 0.5)
                records.append({
                    "date": date,
                    "region_name": point["name"],
                    "lat": point["lat"],
                    "lon": point["lon"],
                    "sst_celsius": round(sst, 2),
                    "source": "INSAT-3D_MOCK",
                })

        return pd.DataFrame(records)

    def _generate_mock_precipitation(self, start: datetime, end: datetime) -> pd.DataFrame:
        """Generate mock INSAT satellite precipitation estimates."""
        import math
        dates = pd.date_range(start=start, end=end, freq="3H")
        records = []
        for date in dates:
            monsoon = 1 + 2.5 * math.exp(-0.5 * ((date.month - 8) / 1.5) ** 2) if 6 <= date.month <= 9 else 0.1
            precip = max(0, np.random.exponential(2.0 * monsoon))
            records.append({
                "timestamp": date,
                "precipitation_mmhr": round(precip, 3),
                "source": "INSAT-3D_MOCK",
                "product": "QPE",  # Quantitative Precipitation Estimate
            })
        return pd.DataFrame(records)

    def _load_hdf5_lst(self, start: datetime, end: datetime) -> pd.DataFrame:
        """
        Load LST from MOSDAC HDF5 files.

        PLUG-IN POINT:
        1. Download HDF5 files from mosdac.gov.in
        2. Set data_path to directory containing .h5 files
        3. This method will parse them using h5py

        HDF5 structure (INSAT-3D): /IMG/LST, /IMG/Latitude, /IMG/Longitude
        """
        try:
            import h5py
            files = list(self.data_path.glob("3RIMG_*.h5"))
            if not files:
                logger.warning("No INSAT HDF5 files found, using mock LST")
                return self._generate_mock_lst(8, 37, 68, 97.5, start, end)

            records = []
            for fpath in files:
                with h5py.File(fpath, "r") as f:
                    # INSAT-3D data structure
                    if "IMG" in f and "LST" in f["IMG"]:
                        lst_data = f["IMG/LST"][:]
                        lat = f["IMG/Latitude"][:]
                        lon = f["IMG/Longitude"][:]
                        timestamp = fpath.stem.split("_")[1]  # parse from filename
                        records.append({
                            "timestamp": timestamp,
                            "lst_data": lst_data,
                            "lat": lat,
                            "lon": lon,
                        })
            return pd.DataFrame(records)
        except Exception as e:
            logger.error(f"HDF5 load failed: {e}")
            return self._generate_mock_lst(8, 37, 68, 97.5, start, end)

    def _load_hdf5_sst(self, start: datetime, end: datetime) -> pd.DataFrame:
        """Load SST from MOSDAC HDF5 — PLUG-IN POINT."""
        return self._generate_mock_sst(start, end)
