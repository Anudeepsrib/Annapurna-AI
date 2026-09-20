from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.safety import WELLNESS_DISCLAIMER
from app.domain.feedback import MealType
from app.domain.planning.replacement import MealLockRequest, MealReplacementRequest, MealReplacementService
from app.models.schemas import PlanRequest
from app.services.plan_service import PlanService

router = APIRouter(tags=["planning"])


@router.post("/generate-plan")
async def generate_plan(
    plan_request: PlanRequest,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    session: AsyncSession = Depends(get_session),
):
    result = await PlanService(session).generate_plan(plan_request, "local-user", idempotency_key)
    return {
        "status": "success",
        "message": "Plan generated and validated for general wellness use",
        "plan": result["plan"],
        "source_status": result["source_status"],
        "disclaimer": result.get("disclaimer", WELLNESS_DISCLAIMER),
        "safety_notes": result.get("safety_notes", []),
        "grocery_optimization": result.get("grocery_optimization", []),
        "generation_metadata": result["generation_metadata"],
    }


@router.get("/plan")
async def get_plan(session: AsyncSession = Depends(get_session)):
    plan = await PlanService(session).get_latest_plan("local-user")
    return plan or []


@router.post("/plan/{day}/{meal_type}/lock")
async def set_meal_lock(
    day: str,
    meal_type: MealType,
    request: MealLockRequest,
    session: AsyncSession = Depends(get_session),
):
    return await MealReplacementService(session).set_locked("local-user", day, meal_type, request.locked)


@router.post("/plan/{day}/{meal_type}/replace")
async def replace_meal(
    day: str,
    meal_type: MealType,
    request: MealReplacementRequest,
    session: AsyncSession = Depends(get_session),
):
    return await MealReplacementService(session).replace("local-user", day, meal_type, request)


@router.post("/plan/{day}/regenerate")
async def regenerate_day(day: str, session: AsyncSession = Depends(get_session)):
    return await MealReplacementService(session).regenerate_day("local-user", day)


@router.get("/grocery-list")
async def get_grocery_list(session: AsyncSession = Depends(get_session)):
    return await PlanService(session).generate_grocery_list("local-user")
