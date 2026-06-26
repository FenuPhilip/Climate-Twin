"""
LSTM Model — Climate Prediction (Rainfall & Temperature)

Architecture:
- 2-layer LSTM (configurable)
- Dropout regularization
- Dense output layer with optional sigmoid/linear activation
- Supports both rainfall (non-negative) and temperature (continuous) targets
"""
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ClimateLSTM(nn.Module):
    """
    LSTM-based climate prediction model.

    Inputs: (batch, seq_len, n_features)
    Output: (batch, 1) — scalar prediction
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        output_activation: str = "linear",  # "linear" | "relu" | "sigmoid"
    ):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_activation = output_activation

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )

        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, 1)
        self.relu = nn.ReLU()
        self.layer_norm = nn.LayerNorm(hidden_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_size)
        lstm_out, _ = self.lstm(x)

        # Use last timestep
        out = lstm_out[:, -1, :]
        out = self.layer_norm(out)
        out = self.dropout(out)
        out = self.relu(self.fc1(out))
        out = self.fc2(out)

        if self.output_activation == "relu":
            out = self.relu(out)  # Non-negative (rainfall)
        elif self.output_activation == "sigmoid":
            out = torch.sigmoid(out)

        return out.squeeze(-1)


class GRUModel(nn.Module):
    """GRU alternative to LSTM — faster training, fewer parameters."""

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, 1)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.gru(x)
        out = self.relu(self.fc(out[:, -1, :]))
        return out.squeeze(-1)


class ModelRegistry:
    """
    Model registry — manages model creation, loading, and saving.
    Supports swapping models without changing prediction pipeline.
    """

    AVAILABLE_MODELS = {
        "lstm": ClimateLSTM,
        "gru": GRUModel,
    }

    @staticmethod
    def create(
        model_type: str,
        input_size: int,
        target: str = "rainfall",
        **kwargs,
    ) -> nn.Module:
        """Create a new model instance."""
        if model_type not in ModelRegistry.AVAILABLE_MODELS:
            raise ValueError(f"Unknown model type: {model_type}. Choose from {list(ModelRegistry.AVAILABLE_MODELS.keys())}")

        model_cls = ModelRegistry.AVAILABLE_MODELS[model_type]

        # Rainfall uses ReLU output (non-negative), temperature uses linear
        if model_type == "lstm":
            activation = "relu" if target == "rainfall" else "linear"
            return model_cls(input_size=input_size, output_activation=activation, **kwargs)

        return model_cls(input_size=input_size, **kwargs)

    @staticmethod
    def save(model: nn.Module, path: Path, metadata: dict = None):
        """Save model state dict and metadata."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        save_dict = {
            "state_dict": model.state_dict(),
            "metadata": metadata or {},
            "model_class": model.__class__.__name__,
        }
        torch.save(save_dict, path)
        logger.info(f"Model saved to {path}")

    @staticmethod
    def load(model: nn.Module, path: Path) -> Tuple[nn.Module, dict]:
        """Load model state dict from file."""
        checkpoint = torch.load(path, map_location="cpu")
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        logger.info(f"Model loaded from {path}")
        return model, checkpoint.get("metadata", {})
