from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.settings import router as settings_router
from app.core.config import settings
from app.core.database import get_session
from app.core.safety import WELLNESS_DISCLAIMER
from app.models.schemas import EvidenceResponse, PlanRequest
from app.services.evidence_service import evidence_service
from app.services.orchestrator import orchestrator
from app.services.plan_service import PlanService
from app.services.usda_client import usda_client

router = APIRouter()

# Include settings routes
router.include_router(settings_router, prefix="/settings")


@router.get("/health")
async def api_health_check():
    return {
        "status": "ok",
        "mode": settings.APP_ENV,
        "external_network_enabled": settings.ENABLE_EXTERNAL_NETWORK,
    }


# --- Plan Generation Routes ---


@router.get("/evidence/{topic}", response_model=EvidenceResponse)
async def get_evidence(topic: str):
    """
    Get evidence for a topic.
    Prioritizes curated guidelines, falls back to PubMed (if enabled).
    """
    return await orchestrator.get_evidence(topic)


@router.get("/mcp/ifct/search")
async def search_ifct(query: str):
    """
    Search local IFCT database.
    """
    results = evidence_service.get_ifct_food(query)
    return {"results": results}


@router.get("/mcp/usda/search")
async def search_usda(query: str):
    """
    Search USDA FoodData Central (if enabled in settings).
    """
    results = await usda_client.search_foods(query)
    return results


@router.post("/generate-plan")
async def generate_plan(
    plan_request: PlanRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Generate a weekly meal plan using LLM + DB Persistence.
    Local mode - no rate limiting needed.
    """
    # Single-user local mode - use static local user
    user_id = "local-user"
    service = PlanService(session)
    result = await service.generate_plan(plan_request, user_id)
    return {
        "status": "success",
        "message": "Plan generated and validated for general wellness use",
        "plan": result["plan"],
        "source_status": result["source_status"],
        "disclaimer": result.get("disclaimer", WELLNESS_DISCLAIMER),
        "safety_notes": result.get("safety_notes", []),
        "grocery_optimization": result.get("grocery_optimization", []),
    }


@router.get("/plan")
async def get_plan(
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve the current meal plan for the user.
    """
    user_id = "local-user"
    service = PlanService(session)
    plan = await service.get_latest_plan(user_id)

    if not plan:
        return []

    return plan


@router.get("/grocery-list")
async def get_grocery_list(
    session: AsyncSession = Depends(get_session),
):
    """
    Generate grocery list from the latest plan.
    """
    user_id = "local-user"
    service = PlanService(session)
    grocery_list = await service.generate_grocery_list(user_id)
    return grocery_list

