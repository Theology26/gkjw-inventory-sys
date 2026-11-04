import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Tentukan lokasi .env secara absolut agar selalu terbaca baik dijalankan dari root maupun folder backend
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BACKEND_DIR.parent

ENV_FILE_PATHS = [
    str(BACKEND_DIR / ".env"),
    str(ROOT_DIR / ".env"),
    ".env"
]


class Settings(BaseSettings):
    APP_NAME: str = "Sistem Inventaris GKJW Sukun"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    # Security & JWT
    JWT_SECRET_KEY: str = "gantidengankuncirahasiayangpanjang2025"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days default for church operations

    # PostgreSQL Database Settings
    DATABASE_URL: str = "postgresql://postgres:theo123@127.0.0.1:5432/gkjw_sukun_inventory"

    # Connection Pool Guardrails (SKILL.md: pool_size=5, max_overflow=10 to preserve laptop RAM)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800

    # Local Storage Engine
    UPLOAD_DIR: str = "storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATHS,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @property
    def items_upload_dir(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "photos", "items")

    @property
    def locations_upload_dir(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "photos", "locations")

    @property
    def documents_upload_dir(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "documents")


settings = Settings()

# Ensure directories exist
os.makedirs(settings.items_upload_dir, exist_ok=True)
os.makedirs(settings.locations_upload_dir, exist_ok=True)
os.makedirs(settings.documents_upload_dir, exist_ok=True)
