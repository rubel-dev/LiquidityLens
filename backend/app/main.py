import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.routes.alerts import router as alerts_router
from app.api.routes.audit_events import router as audit_events_router
from app.api.routes.cases import router as cases_router
from app.api.routes.data_quality import router as data_quality_router
from app.api.routes.findings import router as findings_router
from app.api.routes.forecasts import router as forecasts_router
from app.api.routes.health import router as health_router
from app.api.routes.readiness import router as readiness_router
from app.api.routes.scenarios import router as scenarios_router
from app.api.routes.session import router as session_router
from app.core.config import get_settings
from app.core.errors import error_payload
from app.core.logging import configure_logging
from app.persistence.database import SessionLocal
from app.persistence.seed import ensure_demo_seed

logger = logging.getLogger(__name__)


def _run_migrations() -> None:
    """Run alembic upgrade head using the Python API.

    alembic.ini is expected at the working-directory root (i.e. the backend/
    directory, which FastAPI Cloud sets as the application directory).
    """
    cfg = AlembicConfig("alembic.ini")
    alembic_command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    import asyncio
    logger.info("Running database migrations...")
    try:
        await asyncio.to_thread(_run_migrations)
        logger.info("Migrations complete.")
    except Exception:
        logger.exception("Migration failed — backend may not function correctly")

    logger.info("Seeding demo reference data...")
    try:
        with SessionLocal() as session:
            with session.begin():
                ensure_demo_seed(session)
        logger.info("Demo seed complete.")
    except Exception:
        logger.exception("Demo seed failed — backend may not function correctly")
    yield


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title="LiquidityLens API", version=settings.app_version, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def correlation_id_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = correlation_id
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                code="http_error",
                message=str(exc.detail),
                correlation_id=request.state.correlation_id,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled application error",
            extra={"correlation_id": request.state.correlation_id},
        )
        return JSONResponse(
            status_code=500,
            content=error_payload(
                code="internal_server_error",
                message="An internal error occurred.",
                correlation_id=request.state.correlation_id,
            ),
        )

    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(readiness_router, prefix=settings.api_v1_prefix)
    app.include_router(session_router, prefix=settings.api_v1_prefix)
    app.include_router(scenarios_router, prefix=settings.api_v1_prefix)
    app.include_router(alerts_router, prefix=settings.api_v1_prefix)
    app.include_router(cases_router, prefix=settings.api_v1_prefix)
    app.include_router(forecasts_router, prefix=settings.api_v1_prefix)
    app.include_router(findings_router, prefix=settings.api_v1_prefix)
    app.include_router(data_quality_router, prefix=settings.api_v1_prefix)
    app.include_router(audit_events_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
