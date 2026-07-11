from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.errors import error_payload
from app.persistence.database import check_database_ready

router = APIRouter(tags=["readiness"])


@router.get("/readiness", response_model=None)
def readiness(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, str] | JSONResponse:
    if check_database_ready(settings):
        return {
            "status": "ready",
            "service": settings.app_name,
            "version": settings.app_version,
        }

    return JSONResponse(
        status_code=503,
        content=error_payload(
            code="service_unavailable",
            message="Database is unavailable.",
            correlation_id=request.state.correlation_id,
        ),
    )
