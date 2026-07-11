from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])
SETTINGS_DEPENDENCY = Depends(get_settings)


@router.get("/health")
def health(settings: Settings = SETTINGS_DEPENDENCY) -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
