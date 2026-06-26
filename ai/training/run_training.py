"""
Training CLI — Run model training for ClimateTwin AI

Usage:
    python -m training.run_training --region Kerala --target rainfall --model lstm
    python -m training.run_training --region Delhi --target temperature --model rf
    python -m training.run_training --all  # train all combinations
"""
import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("training_cli")


REGIONS = [
    "Kerala", "Rajasthan", "Tamil Nadu", "Assam", "Delhi",
    "Maharashtra", "West Bengal", "Uttar Pradesh",
]

TARGETS = ["rainfall", "temperature"]


def train_lstm(region: str, target: str, epochs: int = 50, years: int = 5):
    """Train LSTM model."""
    import torch
    from ai.models.lstm_model import ModelRegistry
    from ai.training.trainer import LSTMTrainer

    # Determine input_size based on feature engineering output
    # Using a fixed estimate; training will fail gracefully if wrong
    INPUT_SIZE = 40  # approximate number of features after engineering

    model = ModelRegistry.create(
        model_type="lstm",
        input_size=INPUT_SIZE,
        target=target,
        hidden_size=128,
        num_layers=2,
        dropout=0.2,
    )

    trainer = LSTMTrainer(
        model=model,
        target=target,
        epochs=epochs,
        model_save_dir=Path("./ai/models/saved"),
    )

    logger.info(f"Training LSTM for {region} — {target}")
    result = trainer.train(region=region, years=years)

    logger.info(f"Training complete: {result}")
    from ai.evaluation.metrics import ClimateMetrics
    print(ClimateMetrics.format_report(
        {"val_loss": result["best_val_loss"]},
        target=target,
        region=region,
    ))


def train_rf(region: str, target: str, years: int = 5):
    """Train Random Forest model."""
    from ai.training.trainer import RandomForestTrainer

    trainer = RandomForestTrainer(
        target=target,
        n_estimators=200,
        model_save_dir=Path("./ai/models/saved"),
    )

    logger.info(f"Training RandomForest for {region} — {target}")
    result = trainer.train(region=region, years=years)

    from ai.evaluation.metrics import ClimateMetrics
    print(ClimateMetrics.format_report(result["metrics"], target=target, region=region))


def main():
    parser = argparse.ArgumentParser(description="ClimateTwin AI Training CLI")
    parser.add_argument("--region", choices=REGIONS, default="Kerala")
    parser.add_argument("--target", choices=TARGETS, default="rainfall")
    parser.add_argument("--model", choices=["lstm", "rf", "both"], default="rf")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--years", type=int, default=5)
    parser.add_argument("--all", action="store_true", help="Train all region+target combinations")
    args = parser.parse_args()

    if args.all:
        for region in REGIONS[:3]:  # Train subset for demo
            for target in TARGETS:
                try:
                    if args.model in ("rf", "both"):
                        train_rf(region, target, args.years)
                    if args.model in ("lstm", "both"):
                        train_lstm(region, target, args.epochs, args.years)
                except Exception as e:
                    logger.error(f"Failed {region}/{target}: {e}")
    else:
        if args.model in ("rf", "both"):
            train_rf(args.region, args.target, args.years)
        if args.model in ("lstm", "both"):
            train_lstm(args.region, args.target, args.epochs, args.years)


if __name__ == "__main__":
    main()
