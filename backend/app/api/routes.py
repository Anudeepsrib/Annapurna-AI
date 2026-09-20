from fastapi import APIRouter

from app.api.routers.evidence import router as evidence_router
from app.api.routers.health import router as health_router
from app.api.routers.household import router as household_router
from app.api.routers.pantry import router as pantry_router
from app.api.routers.planning import router as planning_router
from app.api.routers.settings import router as settings_router

router = APIRouter()
router.include_router(health_router)
router.include_router(planning_router)
router.include_router(household_router)
router.include_router(pantry_router)
router.include_router(evidence_router)
router.include_router(settings_router, prefix="/settings")
