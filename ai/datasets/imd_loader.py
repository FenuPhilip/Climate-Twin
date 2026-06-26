"""
IMD Dataset Loader

Supports:
1. Mock data generation (default — for development/hackathon)
2. Real IMD NetCDF files (plug in real path when available)
3. Real IMD API endpoint (plug in API key when available)

The loader always returns a standardized pandas DataFrame regardless of source.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


# India states climate parameters (mirrors backend mock_data_service)
STATE_CLIMATE_PARAMS = {
    "Kerala":        {"temp_mean": 27, "temp_std": 3, "rain_mean": 8.0, "rain_std": 6.0},
    "Rajasthan":     {"temp_mean": 28, "temp_std": 6, "rain_mean": 0.5, "rain_std": 1.0},
    "Tamil Nadu":    {"temp_mean": 29, "temp_std": 3, "rain_mean": 4.0, "rain_std": 4.0},
    "Assam":         {"temp_mean": 25, "temp_std": 4, "rain_mean": 9.0, "rain_std": 7.0},
    "Delhi":         {"temp_mean": 25, "temp_std": 8, "rain_mean": 1.5, "rain_std": 2.5},
    "Maharashtra":   {"temp_mean": 26, "temp_std": 4, "rain_mean": 4.0, "rain_std": 5.0},
    "West Bengal":   {"temp_mean": 26, "temp_std": 5, "rain_mean": 6.0, "rain_std": 5.0},
    "Uttar Pradesh": {"temp_mean": 25, "temp_std": 6, "rain_mean": 2.5, "rain_std": 3.0},
}


def _monsoon_multiplier(month: int) -> float:
    """Monsoon effect: peak in August."""
    import math
    if 6 <= month <= 9:
        return 1.0 + 2.5 * math.exp(-0.5 * ((month - 8) / 1.5) ** 2)
    elif month in [5, 10]:
        return 0.6
    return 0.15


class IMDDataLoader:
    """
    Loads IMD climate data from:
    - Mock generator (default)
    - NetCDF files (path-based)
    - Real IMD API (API key required)
    """

    def __init__(
        self,
        source: str = "mock",      # "mock" | "netcdf" | "api"
        data_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        api_base_url: Optional[str] = None,
    ):
        self.source = source
        self.data_path = data_path
        self.api_key = api_key
        self.api_base_url = api_base_url
        logger.info(f"IMDDataLoader initialized with source={source}")

    def load_rainfall(
        self,
        region: str = "Kerala",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        freq: str = "D",  # D=daily, M=monthly
    ) -> pd.DataFrame:
        """Load rainfall data for a region."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()

        if self.source == "mock":
            return self._generate_mock_rainfall(region, start_date, end_date, freq)
        elif self.source == "netcdf":
            return self._load_netcdf_rainfall(region, start_date, end_date)
        elif self.source == "api":
            return self._fetch_api_rainfall(region, start_date, end_date)
        else:
            raise ValueError(f"Unknown source: {self.source}")

    def load_temperature(
        self,
        region: str = "Kerala",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        freq: str = "D",
    ) -> pd.DataFrame:
        """Load temperature data for a region."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()

        if self.source == "mock":
            return self._generate_mock_temperature(region, start_date, end_date, freq)
        elif self.source == "netcdf":
            return self._load_netcdf_temperature(region, start_date, end_date)
        elif self.source == "api":
            return self._fetch_api_temperature(region, start_date, end_date)
        else:
            raise ValueError(f"Unknown source: {self.source}")

    def _generate_mock_rainfall(
        self, region: str, start: datetime, end: datetime, freq: str
    ) -> pd.DataFrame:
        """Generate scientifically calibrated mock rainfall data."""
        params = STATE_CLIMATE_PARAMS.get(region, STATE_CLIMATE_PARAMS["Maharashtra"])
        dates = pd.date_range(start=start, end=end, freq=freq)
        n = len(dates)

        rainfall = []
        for d in dates:
            monsoon = _monsoon_multiplier(d.month)
            base = params["rain_mean"] * monsoon
            value = max(0, np.random.normal(base, params["rain_std"]))
            # Sporadic heavy rainfall events
            if np.random.random() < 0.05 * monsoon:
                value *= np.random.uniform(3, 8)
            rainfall.append(round(value, 2))

        df = pd.DataFrame({
            "date": dates,
            "rainfall_mm": rainfall,
            "region": region,
            "source": "IMD_MOCK",
            "quality_flag": 0,
        })
        df.set_index("date", inplace=True)
        return df

    def _generate_mock_temperature(
        self, region: str, start: datetime, end: datetime, freq: str
    ) -> pd.DataFrame:
        """Generate mock temperature data with seasonal and diurnal cycles."""
        import math
        params = STATE_CLIMATE_PARAMS.get(region, STATE_CLIMATE_PARAMS["Maharashtra"])
        dates = pd.date_range(start=start, end=end, freq=freq)

        temp_max, temp_min, temp_mean = [], [], []
        for d in dates:
            doy = d.timetuple().tm_yday
            seasonal = params["temp_std"] * math.sin(math.pi * (doy - 80) / 183)
            base = params["temp_mean"] + seasonal + np.random.normal(0, 1.0)
            t_max = base + np.random.uniform(4, 8)
            t_min = base - np.random.uniform(3, 7)
            temp_max.append(round(t_max, 2))
            temp_min.append(round(t_min, 2))
            temp_mean.append(round(base, 2))

        df = pd.DataFrame({
            "date": dates,
            "temp_max_c": temp_max,
            "temp_min_c": temp_min,
            "temp_mean_c": temp_mean,
            "region": region,
            "source": "IMD_MOCK",
            "quality_flag": 0,
        })
        df.set_index("date", inplace=True)
        return df

    def _load_netcdf_rainfall(
        self, region: str, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """
        Load rainfall from IMD NetCDF file.

        PLUG-IN POINT: When real IMD NetCDF data is available:
        1. Set data_path to the directory containing .nc files
        2. This method reads using xarray and extracts region-specific data
        """
        try:
            import xarray as xr
            files = list(self.data_path.glob("rainfall_*.nc"))
            if not files:
                logger.warning("No NetCDF files found, falling back to mock data")
                return self._generate_mock_rainfall(region, start, end, "D")

            ds = xr.open_mfdataset(files, combine="by_coords")
            # Select region by lat/lon bounds (simplified — use actual bounds)
            # This would need real lat/lon lookup for the state
            df = ds["RAINFALL"].to_dataframe().reset_index()
            return df
        except Exception as e:
            logger.error(f"NetCDF load failed: {e}, falling back to mock")
            return self._generate_mock_rainfall(region, start, end, "D")

    def _load_netcdf_temperature(
        self, region: str, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """Load temperature from IMD NetCDF — PLUG-IN POINT for real data."""
        try:
            import xarray as xr
            files = list(self.data_path.glob("temperature_*.nc"))
            if not files:
                return self._generate_mock_temperature(region, start, end, "D")

            ds = xr.open_mfdataset(files, combine="by_coords")
            df = ds.to_dataframe().reset_index()
            return df
        except Exception as e:
            logger.error(f"NetCDF temperature load failed: {e}, falling back to mock")
            return self._generate_mock_temperature(region, start, end, "D")

    def _fetch_api_rainfall(
        self, region: str, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """
        Fetch rainfall from IMD API.

        PLUG-IN POINT: Replace with real IMD API endpoint and authentication.
        """
        try:
            import requests
            if not self.api_key or not self.api_base_url:
                raise ValueError("IMD API key and base URL required")

            response = requests.get(
                f"{self.api_base_url}/rainfall",
                params={
                    "region": region,
                    "start": start.strftime("%Y-%m-%d"),
                    "end": end.strftime("%Y-%m-%d"),
                    "api_key": self.api_key,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data["data"])
        except Exception as e:
            logger.error(f"IMD API call failed: {e}, falling back to mock")
            return self._generate_mock_rainfall(region, start, end, "D")

    def _fetch_api_temperature(
        self, region: str, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """Fetch temperature from IMD API — PLUG-IN POINT for real API."""
        logger.warning("IMD API temperature fetch not yet implemented, using mock")
        return self._generate_mock_temperature(region, start, end, "D")

    def load_combined(
        self,
        region: str = "Kerala",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Load combined rainfall + temperature dataset (joined on date)."""
        rain_df = self.load_rainfall(region, start_date, end_date)
        temp_df = self.load_temperature(region, start_date, end_date)

        combined = temp_df.join(rain_df[["rainfall_mm", "quality_flag"]], how="outer", rsuffix="_rain")
        combined.fillna(method="ffill", inplace=True)
        return combined
