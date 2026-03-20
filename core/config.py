from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Hapn"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-me-in-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    database_url: str = "sqlite:///./hapn.db"
    db_echo: bool = False
    auto_create_tables: bool = True

    cors_origins: List[str] = ["*"]


settings = Settings()
