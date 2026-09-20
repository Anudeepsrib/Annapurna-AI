from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def api_health_check():
    return {
        "status": "ok",
        "mode": settings.APP_ENV,
        "external_network_enabled": settings.ENABLE_EXTERNAL_NETWORK,
    }
