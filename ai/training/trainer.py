"""
Training Pipeline — End-to-end model training for ClimateTwin AI.

Supports:
- LSTM / GRU training (PyTorch)
- Random Forest training (scikit-learn)
- Automatic train/val/test split
- Early stopping
- Learning rate scheduling
- Model checkpointing
"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

from ai.datasets.imd_loader import IMDDataLoader
from ai.preprocessing.feature_engineering import ClimateFeatureEngineer, ClimateNormalizer
from ai.models.lstm_model import ModelRegistry
from ai.models.random_forest_model import RandomForestClimateModel
from ai.evaluation.metrics import ClimateMetrics

logger = logging.getLogger(__name__)


class EarlyStopping:
    def __init__(self, patience: int = 10, min_delta: float = 1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float("inf")
        self.should_stop = False

    def __call__(self, val_loss: float) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop


class LSTMTrainer:
    """Trains LSTM/GRU models on climate data."""

    def __init__(
        self,
        model: nn.Module,
        target: str = "rainfall",
        learning_rate: float = 1e-3,
        batch_size: int = 32,
        epochs: int = 100,
        seq_len: int = 30,
        device: Optional[str] = None,
        model_save_dir: Path = Path("./ai/models/saved"),
    ):
        self.model = model
        self.target = target
        self.lr = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.seq_len = seq_len
        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model.to(self.device)
        self.model_save_dir = Path(model_save_dir)
        self.model_save_dir.mkdir(parents=True, exist_ok=True)

        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, patience=5, factor=0.5, verbose=True
        )
        self.criterion = nn.MSELoss()

        logger.info(f"Trainer initialized on device={self.device}")

    def prepare_data(
        self, region: str = "Kerala", years: int = 5
    ) -> Tuple[DataLoader, DataLoader, DataLoader, ClimateNormalizer]:
        """Load and preprocess data for training."""
        from datetime import timedelta

        loader = IMDDataLoader(source="mock")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        df = loader.load_combined(region=region, start_date=start_date, end_date=end_date)

        # Feature engineering
        engineer = ClimateFeatureEngineer(lookback_days=self.seq_len)
        df_feat = engineer.create_features(df, target_col=self.target)

        # Normalize
        normalizer = ClimateNormalizer()
        feature_cols = engineer.get_feature_names(df_feat, self.target)
        all_cols = feature_cols + [self.target]
        df_norm = normalizer.fit_transform(df_feat[all_cols], all_cols)

        features = df_norm[feature_cols].values
        targets = df_norm[self.target].values

        # Create sequences
        X, y = engineer.create_sequences(features, targets, seq_len=self.seq_len)

        # Train/Val/Test split: 70/15/15
        n = len(X)
        train_end = int(n * 0.70)
        val_end = int(n * 0.85)

        datasets = []
        for X_split, y_split in [
            (X[:train_end], y[:train_end]),
            (X[train_end:val_end], y[train_end:val_end]),
            (X[val_end:], y[val_end:]),
        ]:
            ds = TensorDataset(
                torch.FloatTensor(X_split),
                torch.FloatTensor(y_split),
            )
            is_train = X_split is X[:train_end]
            datasets.append(DataLoader(ds, batch_size=self.batch_size, shuffle=is_train))

        return datasets[0], datasets[1], datasets[2], normalizer

    def train(self, region: str = "Kerala", years: int = 5) -> Dict:
        """Full training loop with early stopping."""
        train_dl, val_dl, test_dl, normalizer = self.prepare_data(region, years)
        early_stopping = EarlyStopping(patience=10)

        history = {"train_loss": [], "val_loss": []}
        best_val_loss = float("inf")

        for epoch in range(self.epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            for X_batch, y_batch in train_dl:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                self.optimizer.zero_grad()
                preds = self.model(X_batch)
                loss = self.criterion(preds, y_batch)
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                train_loss += loss.item()

            train_loss /= len(train_dl)

            # Validation
            self.model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for X_batch, y_batch in val_dl:
                    X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                    preds = self.model(X_batch)
                    val_loss += self.criterion(preds, y_batch).item()
            val_loss /= len(val_dl)

            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)
            self.scheduler.step(val_loss)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                ModelRegistry.save(
                    self.model,
                    self.model_save_dir / f"{self.target}_best.pt",
                    metadata={
                        "region": region,
                        "target": self.target,
                        "epoch": epoch,
                        "val_loss": val_loss,
                        "trained_at": datetime.now().isoformat(),
                    },
                )

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{self.epochs} | Train: {train_loss:.4f} | Val: {val_loss:.4f}")

            if early_stopping(val_loss):
                logger.info(f"Early stopping at epoch {epoch+1}")
                break

        return {
            "history": history,
            "best_val_loss": best_val_loss,
            "target": self.target,
            "region": region,
        }


class RandomForestTrainer:
    """Trains Random Forest models (faster, no GPU required)."""

    def __init__(
        self,
        target: str = "rainfall",
        n_estimators: int = 200,
        model_save_dir: Path = Path("./ai/models/saved"),
    ):
        self.target = target
        self.n_estimators = n_estimators
        self.model_save_dir = Path(model_save_dir)
        self.model_save_dir.mkdir(parents=True, exist_ok=True)

    def train(self, region: str = "Kerala", years: int = 5) -> Dict:
        """Train Random Forest model."""
        from datetime import timedelta

        loader = IMDDataLoader(source="mock")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)
        df = loader.load_combined(region=region, start_date=start_date, end_date=end_date)

        engineer = ClimateFeatureEngineer()
        df_feat = engineer.create_features(df, target_col=self.target)

        feature_cols = engineer.get_feature_names(df_feat, self.target)
        X = df_feat[feature_cols].values
        y = df_feat[self.target].values

        # 80/20 split
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        model = RandomForestClimateModel(
            n_estimators=self.n_estimators,
            target=self.target,
        )
        model.fit(X_train, y_train, feature_names=feature_cols)

        preds = model.predict(X_test)
        metrics = ClimateMetrics.compute(y_test, preds)

        model.save(self.model_save_dir / f"rf_{self.target}.pkl")

        logger.info(f"RandomForest training complete: {metrics}")
        return {"metrics": metrics, "target": self.target, "region": region}
