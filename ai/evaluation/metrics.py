"""
Evaluation Metrics — Model validation for climate predictions.

Metrics:
- MAE: Mean Absolute Error
- RMSE: Root Mean Squared Error
- R²: Coefficient of Determination
- Skill Score: vs climatological mean baseline
- Prediction Accuracy: within threshold
"""
import numpy as np
from typing import Dict, Optional
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class ClimateMetrics:
    """Compute evaluation metrics for climate predictions."""

    @staticmethod
    def compute(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        threshold: float = 1.0,
    ) -> Dict[str, float]:
        """
        Compute all evaluation metrics.

        Args:
            y_true: Ground truth values
            y_pred: Model predictions
            threshold: Acceptable error threshold for accuracy calculation

        Returns:
            Dict with MAE, RMSE, R², and other metrics
        """
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)

        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)

        # Prediction accuracy: % within threshold
        within_threshold = np.mean(np.abs(y_true - y_pred) <= threshold) * 100

        # Bias
        bias = np.mean(y_pred - y_true)

        # Skill score vs persistence (previous day as forecast)
        persistence = y_true[:-1]
        persistence_rmse = np.sqrt(mean_squared_error(y_true[1:], persistence))
        skill_score = 1 - (rmse / max(persistence_rmse, 1e-6))

        return {
            "mae": round(float(mae), 4),
            "rmse": round(float(rmse), 4),
            "r2_score": round(float(r2), 4),
            "accuracy_pct": round(float(within_threshold), 2),
            "bias": round(float(bias), 4),
            "skill_score": round(float(skill_score), 4),
            "sample_count": int(len(y_true)),
        }

    @staticmethod
    def compute_confidence_interval(
        predictions: np.ndarray,
        confidence: float = 0.95,
    ) -> Dict[str, np.ndarray]:
        """
        Estimate prediction confidence intervals using ensemble spread.

        For a single model, uses bootstrap estimate.
        """
        from scipy import stats
        se = stats.sem(predictions)
        interval = stats.t.interval(
            confidence,
            df=len(predictions) - 1,
            loc=np.mean(predictions),
            scale=se,
        )
        return {
            "lower": float(interval[0]),
            "upper": float(interval[1]),
            "mean": float(np.mean(predictions)),
            "std": float(np.std(predictions)),
        }

    @staticmethod
    def format_report(metrics: Dict, target: str, region: str) -> str:
        """Format metrics as a readable report string."""
        return (
            f"\n{'='*50}\n"
            f"Model Evaluation Report\n"
            f"Target: {target} | Region: {region}\n"
            f"{'='*50}\n"
            f"MAE:           {metrics.get('mae', 'N/A')}\n"
            f"RMSE:          {metrics.get('rmse', 'N/A')}\n"
            f"R² Score:      {metrics.get('r2_score', 'N/A')}\n"
            f"Accuracy (%):  {metrics.get('accuracy_pct', 'N/A')}\n"
            f"Bias:          {metrics.get('bias', 'N/A')}\n"
            f"Skill Score:   {metrics.get('skill_score', 'N/A')}\n"
            f"Samples:       {metrics.get('sample_count', 'N/A')}\n"
            f"{'='*50}\n"
        )
