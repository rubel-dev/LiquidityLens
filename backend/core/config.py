from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# .env lives at project root (one level above backend/)
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL_FAST: str = "gpt-4o-mini"
    OPENAI_MODEL_SMART: str = "gpt-4o"

    # Database
    DATABASE_URL: str        # asyncpg pooled — runtime
    DATABASE_SYNC_URL: str   # psycopg2 direct — alembic migrations

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Provider simulation (Scenario C)
    NAGAD_DELAY_SECONDS: int = 0
    BKASH_FAILURE_MODE: bool = False
    ROCKET_DELAY_SECONDS: int = 0

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
