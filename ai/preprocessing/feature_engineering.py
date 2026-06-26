"""
Feature Engineering Pipeline — Transforms raw climate data into ML-ready features.

Features generated:
- Lag features (1, 3, 7, 14, 30 day lags)
- Rolling statistics (7-day, 30-day mean, std)
- Seasonal encodings (sin/cos of day-of-year, month)
- Monsoon indicators
- Interaction features (temp × humidity)
"""
import numpy as np
import pandas as pd
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ClimateFeatureEngineer:
    """
    Transforms raw IMD/INSAT observations into feature vectors for ML models.
    """

    def __init__(self, lookback_days: int = 30, horizon_days: int = 1):
        self.lookback_days = lookback_days
        self.horizon_days = horizon_days

    def create_features(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Create complete feature set from time series data.

        Args:
            df: DataFrame with DatetimeIndex, containing climate parameters
            target_col: Column to predict (e.g., 'rainfall_mm', 'temp_max_c')

        Returns:
            DataFrame with engineered features + target column
        """
        df = df.copy()
        df = df.sort_index()

        # --- Temporal encodings ---
        df["day_of_year"] = df.index.dayofyear
        df["month"] = df.index.month
        df["day_of_week"] = df.index.dayofweek
        df["year"] = df.index.year

        # Sin/cos encoding for cyclical features
        df["doy_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
        df["doy_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

        # Monsoon indicator
        df["is_monsoon"] = df["month"].isin([6, 7, 8, 9]).astype(float)

        # --- Lag features ---
        for lag in [1, 2, 3, 7, 14, 30]:
            if lag <= len(df):
                df[f"{target_col}_lag{lag}"] = df[target_col].shift(lag)

        # --- Rolling statistics ---
        for window in [7, 14, 30]:
            df[f"{target_col}_roll{window}_mean"] = (
                df[target_col].shift(1).rolling(window).mean()
            )
            df[f"{target_col}_roll{window}_std"] = (
                df[target_col].shift(1).rolling(window).std()
            )
            df[f"{target_col}_roll{window}_max"] = (
                df[target_col].shift(1).rolling(window).max()
            )

        # --- Exponential moving average ---
        df[f"{target_col}_ema7"] = (
            df[target_col].shift(1).ewm(span=7, adjust=False).mean()
        )
        df[f"{target_col}_ema30"] = (
            df[target_col].shift(1).ewm(span=30, adjust=False).mean()
        )

        # --- Interaction features (if both present) ---
        if "temp_mean_c" in df.columns and "rainfall_mm" in df.columns:
            df["temp_x_rainfall"] = df["temp_mean_c"] * df["rainfall_mm"]

        # --- Drop rows with NaN from lags ---
        df.dropna(inplace=True)

        logger.info(f"Feature engineering complete. Shape: {df.shape}, Features: {len(df.columns)}")
        return df

    def create_sequences(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        seq_len: int = 30,
    ):
        """
        Create sliding window sequences for LSTM training.

        Returns:
            X: shape (samples, seq_len, features)
            y: shape (samples,)
        """
        X, y = [], []
        for i in range(seq_len, len(features)):
            X.append(features[i - seq_len:i])
            y.append(targets[i])
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

    def get_feature_names(self, df: pd.DataFrame, target_col: str) -> List[str]:
        """Return list of feature column names (excluding target)."""
        return [c for c in df.columns if c != target_col]


class ClimateNormalizer:
    """Min-max normalization with state persistence for inverse transform."""

    def __init__(self):
        self._stats: dict = {}

    def fit_transform(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize specified columns and store stats."""
        df = df.copy()
        for col in columns:
            if col in df.columns:
                min_val = df[col].min()
                max_val = df[col].max()
                self._stats[col] = {"min": min_val, "max": max_val}
                range_val = max_val - min_val
                if range_val > 0:
                    df[col] = (df[col] - min_val) / range_val
                else:
                    df[col] = 0.0
        return df

    def inverse_transform(self, values: np.ndarray, column: str) -> np.ndarray:
        """Reverse normalization for a column."""
        if column not in self._stats:
            return values
        stats = self._stats[column]
        return values * (stats["max"] - stats["min"]) + stats["min"]

    def save(self, path: str):
        """Save normalizer stats to file."""
        import json
        with open(path, "w") as f:
            json.dump(self._stats, f)

    def load(self, path: str):
        """Load normalizer stats from file."""
        import json
        with open(path) as f:
            self._stats = json.load(f)
