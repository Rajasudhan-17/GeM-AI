from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "VERIFI – GeM Bid Compliance Verification Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ]
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MOCK_DATA_DIR: Path = BASE_DIR / "mock_data"
    
    # Storage
    MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
    ]
    
    # Queue Mode: local / celery
    QUEUE_MODE: str = "local"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Scoring Weights (Total = 100)
    WEIGHT_GST: float = 15.0
    WEIGHT_UDYAM: float = 10.0
    WEIGHT_PAN: float = 15.0
    WEIGHT_EPFO: float = 10.0
    WEIGHT_ESIC: float = 10.0
    WEIGHT_OEM: float = 15.0
    WEIGHT_DIGILOCKER: float = 10.0
    WEIGHT_BLACKLIST: float = 15.0
    
    # Partial score ratio for REVIEW status
    REVIEW_SCORE_RATIO: float = 0.50  # 50% partial points for REVIEW
    
    # Risk Thresholds
    RISK_THRESHOLD_LOW: float = 85.0
    RISK_THRESHOLD_MEDIUM: float = 60.0
    
    # AI Provider
    AI_PROVIDER: str = "mock"  # mock / openai / anthropic / gemini
    AI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
