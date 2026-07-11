import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.routes.alerts import router as alerts_router
from app.api.routes.cases import router as cases_router
from app.api.routes.health import router as health_router
from app.api.routes.readiness import router as readiness_router
from app.core.config import get_settings
from app.core.errors import error_payload
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title="LiquidityLens API", version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
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
    app.include_router(alerts_router, prefix=settings.api_v1_prefix)
    app.include_router(cases_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
