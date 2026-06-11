"""Centralised application settings loaded from environment / .env."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_name: str = "AI Interview Assistant"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me"

    # JWT
    jwt_secret_key: str = "change-me-too"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Database parts
    postgres_user: str = "interview"
    postgres_password: str = "interview"
    postgres_db: str = "interview_db"
    postgres_host: str = "db"
    postgres_port: int = 5432
    database_url: str | None = None  # optional explicit override

    # Uploads
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 5

    # Admin bootstrap
    first_admin_email: str = "admin@interview.ai"
    first_admin_password: str = "Admin12345!"

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
