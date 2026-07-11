from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="local", validation_alias="APP_ENV")
    app_name: str = Field(default="liquiditylens-api", validation_alias="APP_NAME")
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@postgres:5432/liquiditylens_demo",
        validation_alias="DATABASE_URL",
    )
    database_sync_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@postgres:5432/liquiditylens_demo",
        validation_alias="DATABASE_SYNC_URL",
    )
    llm_explanation_provider: str = Field(
        default="none",
        validation_alias="LLM_EXPLANATION_PROVIDER",
    )
    llm_explanation_enabled: bool = Field(
        default=False,
        validation_alias="LLM_EXPLANATION_ENABLED",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

