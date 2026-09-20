from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.feedback.models import (
    EmptyTodayView,
    FeedbackRequest,
    FeedbackSignal,
    LeftoverUpdateRequest,
    LeftoverView,
    MealActivityView,
    MealStatus,
    MealStatusRequest,
    MealType,
    TodayView,
)
from app.domain.grocery import GroceryCompiler
from app.domain.pantry import PantryService
from app.models.db import LeftoverRecord, MealPlan
from app.models.schemas import ManualShoppingItem, PlanMeal
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.plan_repository import PlanRepository


class TodayService:
    def __init__(self, session: AsyncSession):
        self.plans = PlanRepository(session)
        self.feedback = FeedbackRepository(session)
        self.pantry = PantryService(session)
        self.grocery = GroceryCompiler()

    async def get_today(self, user_id: str) -> TodayView | EmptyTodayView:
        saved = await self.plans.get_latest(user_id)
        leftovers = [self._leftover_view(item) for item in await self.feedback.list_active_leftovers(user_id)]
        today_name = datetime.now(UTC).strftime("%A")
        if saved is None:
            return EmptyTodayView(day=today_name, date=datetime.now(UTC).date().isoformat(), leftovers=leftovers)

        day = self._select_day(saved)
        plan_id = self._plan_id(saved)
        executions = {
            item.meal_type: MealStatus(item.status)
            for item in await self.feedback.list_executions(user_id, plan_id, day["day"])
        }
        signals: dict[str, list[FeedbackSignal]] = {}
        for item in await self.feedback.list_feedback(user_id, plan_id, day["day"]):
            signals.setdefault(item.meal_type, []).append(FeedbackSignal(item.signal))

        pantry_legacy = await self.pantry.current_legacy_items(user_id)
        payload = saved.plan_data if isinstance(saved.plan_data, dict) else {}
        manual = [
            ManualShoppingItem.model_validate(item)
            for item in payload.get("manual_shopping_items", [])
            if isinstance(item, dict)
        ]
        grocery = self.grocery.compile(
            self._plan(saved),
            pantry_legacy,
            manual,
            payload.get("shopping_exclusions", []),
            payload.get("use_soon_requests", []),
        )
        missing_by_meal: dict[str, list[str]] = {}
        for category in grocery:
            for item in category["items"]:
                if item["status"] != "need_to_buy":
                    continue
                for title in item["meals"]:
                    missing_by_meal.setdefault(title, []).append(item["name"])

        meals = [
            MealActivityView(
                mealType=meal_type,
                meal=PlanMeal.model_validate(day["meals"][meal_type.value]),
                status=executions.get(meal_type.value),
                feedback=signals.get(meal_type.value, []),
                missingIngredients=missing_by_meal.get(day["meals"][meal_type.value]["title"], []),
            )
            for meal_type in MealType
        ]
        pantry = await self.pantry.list_items(user_id)
        expiring = [item for item in pantry if _is_expiring(item.expiresAt, item.expired)]
        return TodayView(
            day=day["day"],
            date=day["date"],
            meals=meals,
            expiringPantry=expiring,
            leftovers=leftovers,
        )

    async def set_status(
        self,
        user_id: str,
        day: str,
        meal_type: MealType,
        request: MealStatusRequest,
    ) -> MealStatus:
        saved, meal = await self._meal_slot(user_id, day, meal_type)
        await self.feedback.set_execution(user_id, self._plan_id(saved), day, meal_type.value, request.status.value)
        if request.status == MealStatus.LEFTOVER:
            await self.feedback.upsert_leftover(
                user_id=user_id,
                plan_id=self._plan_id(saved),
                day=day,
                meal_type=meal_type.value,
                title=meal["title"],
                servings_remaining=request.servingsRemaining or 1,
                usable_until=request.usableUntil or datetime.now(UTC) + timedelta(days=2),
            )
        return request.status

    async def record_feedback(
        self,
        user_id: str,
        day: str,
        meal_type: MealType,
        request: FeedbackRequest,
    ) -> FeedbackSignal:
        saved, _meal = await self._meal_slot(user_id, day, meal_type)
        await self.feedback.add_feedback(
            user_id,
            self._plan_id(saved),
            day,
            meal_type.value,
            request.signal.value,
        )
        return request.signal

    async def list_leftovers(self, user_id: str) -> list[LeftoverView]:
        return [self._leftover_view(item) for item in await self.feedback.list_active_leftovers(user_id)]

    async def update_leftover(
        self,
        user_id: str,
        leftover_id: int,
        request: LeftoverUpdateRequest,
    ) -> LeftoverView:
        record = await self.feedback.get_leftover(user_id, leftover_id)
        if record is None:
            raise NotFoundError("Leftover")
        updated = await self.feedback.update_leftover(
            record,
            request.servingsRemaining,
            request.usableUntil,
            request.consumed,
        )
        return self._leftover_view(updated)

    async def assign_leftover(
        self,
        user_id: str,
        leftover_id: int,
        day: str,
        meal_type: MealType,
    ) -> dict:
        leftover = await self.feedback.get_leftover(user_id, leftover_id)
        usable_until = (
            leftover.usable_until.replace(tzinfo=UTC)
            if leftover is not None and leftover.usable_until.tzinfo is None
            else leftover.usable_until
            if leftover is not None
            else None
        )
        if leftover is None or leftover.consumed or usable_until is None or usable_until < datetime.now(UTC):
            raise NotFoundError("Active leftover")
        saved, _meal = await self._meal_slot(user_id, day, meal_type)
        payload = saved.plan_data
        if not isinstance(payload, dict):
            payload = {"schema_version": 1, "plan": payload}
        selected = next(item for item in payload["plan"] if item.get("day") == day)
        selected["meals"][meal_type.value] = PlanMeal(
            title=f"Leftovers: {leftover.title}",
            description=f"Use {leftover.servings_remaining} saved serving(s) before the use-by date.",
            ingredients=["prepared leftover"],
            time={MealType.BREAKFAST: "8:00 AM", MealType.LUNCH: "1:00 PM", MealType.DINNER: "7:30 PM"}[
                meal_type
            ],
            source_status="leftover_reference",
            leftoverId=leftover_id,
        ).model_dump(mode="json")
        pantry = await self.pantry.current_legacy_items(user_id)
        manual = [
            ManualShoppingItem.model_validate(item)
            for item in payload.get("manual_shopping_items", [])
            if isinstance(item, dict)
        ]
        payload["grocery_optimization"] = self.grocery.compile(
            payload["plan"],
            pantry,
            manual,
            payload.get("shopping_exclusions", []),
            payload.get("use_soon_requests", []),
        )
        payload["schema_version"] = max(int(payload.get("schema_version", 1)), 5)
        await self.plans.update_payload(saved, payload)
        return selected["meals"][meal_type.value]

    async def _meal_slot(self, user_id: str, day: str, meal_type: MealType) -> tuple[MealPlan, dict]:
        saved = await self.plans.get_latest(user_id)
        if saved is None:
            raise NotFoundError("Meal plan")
        selected = next((item for item in self._plan(saved) if item.get("day") == day), None)
        meal = selected.get("meals", {}).get(meal_type.value) if selected else None
        if not isinstance(meal, dict):
            raise NotFoundError("Meal slot")
        return saved, meal

    def _select_day(self, saved: MealPlan) -> dict:
        plan = self._plan(saved)
        today = datetime.now(UTC).strftime("%A")
        return next((day for day in plan if day.get("day") == today), plan[0])

    def _plan(self, saved: MealPlan) -> list[dict]:
        payload = saved.plan_data
        plan = payload.get("plan", []) if isinstance(payload, dict) else payload
        if not isinstance(plan, list) or not plan:
            raise NotFoundError("Meal plan")
        return plan

    def _plan_id(self, saved: MealPlan) -> int:
        if saved.id is None:
            raise NotFoundError("Meal plan")
        return saved.id

    def _leftover_view(self, item: LeftoverRecord) -> LeftoverView:
        return LeftoverView(
            id=item.id,
            title=item.title,
            sourceDay=item.source_day,
            sourceMealType=MealType(item.source_meal_type),
            servingsRemaining=item.servings_remaining,
            createdAt=item.created_at,
            usableUntil=item.usable_until,
        )


def _is_expiring(expires_at: datetime | None, expired: bool) -> bool:
    if expires_at is None or expired:
        return False
    value = expires_at.replace(tzinfo=UTC) if expires_at.tzinfo is None else expires_at.astimezone(UTC)
    return value <= datetime.now(UTC) + timedelta(days=5)
