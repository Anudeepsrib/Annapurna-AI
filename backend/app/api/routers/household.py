from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.commands import HouseholdCommandRequest, HouseholdCommandService
from app.domain.feedback import FeedbackRequest, LeftoverUpdateRequest, MealStatusRequest, MealType, TodayService

router = APIRouter(tags=["household"])


@router.post("/commands")
async def execute_household_command(
    request: HouseholdCommandRequest,
    session: AsyncSession = Depends(get_session),
):
    return await HouseholdCommandService(session).execute("local-user", request)


@router.get("/today")
async def get_today(session: AsyncSession = Depends(get_session)):
    return await TodayService(session).get_today("local-user")


@router.post("/today/{day}/{meal_type}/status")
async def set_meal_status(
    day: str,
    meal_type: MealType,
    request: MealStatusRequest,
    session: AsyncSession = Depends(get_session),
):
    status_value = await TodayService(session).set_status("local-user", day, meal_type, request)
    return {"status": status_value}


@router.post("/today/{day}/{meal_type}/feedback")
async def record_meal_feedback(
    day: str,
    meal_type: MealType,
    request: FeedbackRequest,
    session: AsyncSession = Depends(get_session),
):
    signal = await TodayService(session).record_feedback("local-user", day, meal_type, request)
    return {"signal": signal}


@router.get("/leftovers")
async def get_leftovers(session: AsyncSession = Depends(get_session)):
    return await TodayService(session).list_leftovers("local-user")


@router.patch("/leftovers/{leftover_id}")
async def update_leftover(
    leftover_id: int,
    request: LeftoverUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    return await TodayService(session).update_leftover("local-user", leftover_id, request)


@router.post("/leftovers/{leftover_id}/use/{day}/{meal_type}")
async def assign_leftover(
    leftover_id: int,
    day: str,
    meal_type: MealType,
    session: AsyncSession = Depends(get_session),
):
    return await TodayService(session).assign_leftover("local-user", leftover_id, day, meal_type)
