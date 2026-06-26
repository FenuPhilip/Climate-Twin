"""
Random Forest Baseline Model — Climate Prediction

Used as:
1. A strong baseline against LSTM
2. An ensemble component
3. Fast inference for real-time prediction when LSTM is too slow

Wraps scikit-learn RandomForestRegressor with the same interface as the LSTM models.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
import joblib
import logging

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


class RandomForestClimateModel:
    """
    Random Forest wrapper with same interface as PyTorch models.
    Handles tabular feature input (no sequences needed).
    """

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 15,
        target: str = "rainfall",
        use_gradient_boosting: bool = False,
    ):
        self.target = target
        self.use_gradient_boosting = use_gradient_boosting

        if use_gradient_boosting:
            estimator = GradientBoostingRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42,
            )
        else:
            estimator = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                n_jobs=-1,
                random_state=42,
            )

        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", estimator),
        ])

        self.feature_names: Optional[list] = None
        self.is_trained: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[list] = None):
        """Train the model."""
        self.feature_names = feature_names
        self.pipeline.fit(X, y)
        self.is_trained = True
        logger.info(f"RandomForest trained on {X.shape[0]} samples, {X.shape[1]} features")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions."""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call fit() first.")
        preds = self.pipeline.predict(X)
        if self.target == "rainfall":
            preds = np.maximum(preds, 0.0)
        return preds

    def get_feature_importance(self) -> Dict[str, float]:
        """Return feature importance scores."""
        if not self.is_trained:
            return {}
        model = self.pipeline.named_steps["model"]
        importances = model.feature_importances_
        if self.feature_names:
            return dict(zip(self.feature_names, importances))
        return {f"feature_{i}": v for i, v in enumerate(importances)}

    def save(self, path: Path):
        """Save model to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "pipeline": self.pipeline,
            "feature_names": self.feature_names,
            "target": self.target,
            "is_trained": self.is_trained,
        }, path)
        logger.info(f"RandomForest saved to {path}")

    @classmethod
    def load(cls, path: Path) -> "RandomForestClimateModel":
        """Load model from disk."""
        data = joblib.load(path)
        instance = cls(target=data["target"])
        instance.pipeline = data["pipeline"]
        instance.feature_names = data["feature_names"]
        instance.is_trained = data["is_trained"]
        logger.info(f"RandomForest loaded from {path}")
        return instance
