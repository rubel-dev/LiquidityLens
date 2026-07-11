from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


def create_sync_engine(settings: Settings | None = None) -> Engine:
    active_settings = settings or get_settings()
    return create_engine(active_settings.database_sync_url, pool_pre_ping=True)


engine = create_sync_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_ready(settings: Settings | None = None) -> bool:
    try:
        readiness_engine = create_sync_engine(settings)
        with readiness_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        readiness_engine.dispose()
    except Exception:
        return False
    return True

