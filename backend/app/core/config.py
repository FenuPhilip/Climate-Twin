"""
Application configuration — reads from environment variables.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.example",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://climatetwin:climatetwin_password@localhost:5432/climatetwin"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "climatetwin"
    MINIO_SECRET_KEY: str = "climatetwin_secret"
    MINIO_BUCKET_DATASETS: str = "climate-datasets"
    MINIO_BUCKET_MODELS: str = "ai-models"
    MINIO_SECURE: bool = False

    # AI
    MODEL_STORAGE_PATH: str = "./ai/models/saved"
    AI_PREDICTION_HORIZON_DAYS: int = 7
    TRAINING_LOOKBACK_DAYS: int = 30

    # Data Sources
    IMD_API_BASE_URL: str = ""
    IMD_API_KEY: str = ""
    MOSDAC_API_BASE_URL: str = ""
    MOSDAC_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Twin Scheduler
    TWIN_UPDATE_INTERVAL_SECONDS: int = 300  # 5 minutes

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
