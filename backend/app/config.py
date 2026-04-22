from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://preisopt:preisopt@localhost:5432/preisopt"
    session_secret: str = "change-me"
    app_env: str = "development"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    frontend_dir: str = str(Path(__file__).resolve().parents[2] / "frontend")
    suggestion_ttl_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()
