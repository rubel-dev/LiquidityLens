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
    validation_feed_delay_minutes: int = Field(
        default=5,
        validation_alias="VALIDATION_FEED_DELAY_MINUTES",
    )
    validation_stale_minutes: int = Field(default=15, validation_alias="VALIDATION_STALE_MINUTES")
    validation_future_tolerance_minutes: int = Field(
        default=5,
        validation_alias="VALIDATION_FUTURE_TOLERANCE_MINUTES",
    )
    validation_timestamp_skew_minutes: int = Field(
        default=2,
        validation_alias="VALIDATION_TIMESTAMP_SKEW_MINUTES",
    )
    validation_max_metadata_keys: int = Field(
        default=12,
        validation_alias="VALIDATION_MAX_METADATA_KEYS",
    )
    validation_max_metadata_value_length: int = Field(
        default=120,
        validation_alias="VALIDATION_MAX_METADATA_VALUE_LENGTH",
    )
    validation_supported_currencies: str = Field(
        default="BDT",
        validation_alias="VALIDATION_SUPPORTED_CURRENCIES",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
