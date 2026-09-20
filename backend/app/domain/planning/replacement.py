from copy import deepcopy
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PlanConflictError
from app.core.safety import NUTRITION_ESTIMATE_DISCLAIMER
from app.domain.feedback import MealType
from app.domain.grocery import GroceryCompiler
from app.domain.pantry import PantryService
from app.domain.planning.constraints import ConstraintEngine
from app.domain.planning.models import CompiledConstraints, PlanningPreferences
from app.domain.planning.scorer import PlanScorer
from app.domain.planning.validator import PlanValidator
from app.domain.recipes import recipes_for_meal_type
from app.models.schemas import ManualShoppingItem, PlanMeal, PlanRequest
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.plan_repository import PlanRepository


class MealLockRequest(BaseModel):
    locked: bool


class MealReplacementRequest(BaseModel):
    note: str = Field(default="", max_length=300)


class MealReplacementService:
    def __init__(self, session: AsyncSession):
        self.plans = PlanRepository(session)
        self.feedback = FeedbackRepository(session)
        self.pantry = PantryService(session)
        self.validator = PlanValidator()
        self.scorer = PlanScorer()
        self.grocery = GroceryCompiler()

    async def set_locked(self, user_id: str, day: str, meal_type: MealType, locked: bool) -> dict:
        saved, payload, _plan, meal = await self._slot(user_id, day, meal_type)
        meal["locked"] = locked
        payload["schema_version"] = max(int(payload.get("schema_version", 1)), 4)
        await self.plans.update_payload(saved, payload)
        return meal

    async def replace(
        self,
        user_id: str,
        day: str,
        meal_type: MealType,
        request: MealReplacementRequest,
    ) -> dict[str, Any]:
        saved, payload, plan, current = await self._slot(user_id, day, meal_type)
        if current.get("locked"):
            raise PlanConflictError("Locked meals must be unlocked before replacement")

        constraints, preferences = self._rules(payload)
        pantry = await self.pantry.current_legacy_items(user_id)
        feedback_weights = await self.feedback.preference_weights(user_id)
        selected = self._replace_in_plan(
            plan,
            day,
            meal_type,
            constraints,
            preferences,
            pantry,
            feedback_weights,
            request.note,
        )
        replacement = next(item for item in selected if item.get("day") == day)["meals"][meal_type.value]
        plan[:] = selected
        grocery = self._compile_grocery(plan, pantry, payload)
        payload.update(
            {
                "schema_version": max(int(payload.get("schema_version", 1)), 4),
                "plan": plan,
                "grocery_optimization": grocery,
            }
        )
        payload.setdefault("replacement_history", []).append(
            {"day": day, "meal_type": meal_type.value, "from": current.get("title"), "to": replacement["title"]}
        )
        await self.plans.update_payload(saved, payload)
        return {"meal": replacement, "plan": plan, "grocery_optimization": grocery}

    async def regenerate_day(self, user_id: str, day: str) -> dict[str, Any]:
        saved = await self.plans.get_latest(user_id)
        if saved is None:
            raise NotFoundError("Meal plan")
        payload = saved.plan_data
        if isinstance(payload, list):
            payload = {"schema_version": 1, "plan": payload}
        plan = payload.get("plan", [])
        selected_day = next((item for item in plan if item.get("day") == day), None)
        if selected_day is None:
            raise NotFoundError("Plan day")
        constraints, preferences = self._rules(payload)
        pantry = await self.pantry.current_legacy_items(user_id)
        feedback_weights = await self.feedback.preference_weights(user_id)
        regenerated = deepcopy(plan)
        changed: list[str] = []
        for meal_type in MealType:
            meal = selected_day.get("meals", {}).get(meal_type.value, {})
            if meal.get("locked"):
                continue
            regenerated = self._replace_in_plan(
                regenerated,
                day,
                meal_type,
                constraints,
                preferences,
                pantry,
                feedback_weights,
                "",
            )
            changed.append(meal_type.value)
        grocery = self._compile_grocery(regenerated, pantry, payload)
        payload.update(
            {
                "schema_version": max(int(payload.get("schema_version", 1)), 5),
                "plan": regenerated,
                "grocery_optimization": grocery,
            }
        )
        await self.plans.update_payload(saved, payload)
        return {"day": day, "changed": changed, "plan": regenerated, "grocery_optimization": grocery}

    async def _slot(self, user_id: str, day: str, meal_type: MealType):
        saved = await self.plans.get_latest(user_id)
        if saved is None:
            raise NotFoundError("Meal plan")
        payload = saved.plan_data
        if isinstance(payload, list):
            payload = {"schema_version": 1, "plan": payload}
        plan = payload.get("plan", [])
        selected = next((item for item in plan if item.get("day") == day), None)
        meal = selected.get("meals", {}).get(meal_type.value) if selected else None
        if not isinstance(meal, dict):
            raise NotFoundError("Meal slot")
        return saved, payload, plan, meal

    def _rules(self, payload: dict) -> tuple[CompiledConstraints, PlanningPreferences]:
        if payload.get("compiled_constraints"):
            constraints = CompiledConstraints.model_validate(payload["compiled_constraints"])
        else:
            request = PlanRequest(teluguAndhraConstraints=payload.get("telugu_andhra_constraints", []))
            constraints = ConstraintEngine().compile(request)
        preferences = PlanningPreferences.model_validate(payload.get("planning_preferences", {}))
        return constraints, preferences

    def _replace_in_plan(
        self,
        plan: list[dict[str, Any]],
        day: str,
        meal_type: MealType,
        constraints: CompiledConstraints,
        preferences: PlanningPreferences,
        pantry: list,
        feedback_weights: dict[str, float],
        note: str,
    ) -> list[dict[str, Any]]:
        used_titles = {
            meal.get("title", "").casefold()
            for planned_day in plan
            for meal in planned_day.get("meals", {}).values()
        }
        candidates = []
        for replacement in _replacement_options(meal_type, note):
            if replacement["title"].casefold() in used_titles:
                continue
            candidate = deepcopy(plan)
            slot = next(item for item in candidate if item.get("day") == day)
            slot["meals"][meal_type.value] = replacement
            try:
                candidates.append(self.validator.validate(candidate, constraints))
            except ValueError:
                continue
        if not candidates:
            raise PlanConflictError("No valid replacement satisfies the active hard constraints")
        return self.scorer.select_best(candidates, preferences, pantry, feedback_weights)

    def _compile_grocery(self, plan: list[dict[str, Any]], pantry: list, payload: dict) -> list[dict[str, Any]]:
        manual = [
            ManualShoppingItem.model_validate(item)
            for item in payload.get("manual_shopping_items", [])
            if isinstance(item, dict)
        ]
        return self.grocery.compile(
            plan,
            pantry,
            manual,
            payload.get("shopping_exclusions", []),
            payload.get("use_soon_requests", []),
        )


def _replacement_options(meal_type: MealType, note: str = "") -> list[dict[str, Any]]:
    recipes = recipes_for_meal_type(meal_type.value)
    normalized_note = note.casefold()
    if "easier" in normalized_note or "easy" in normalized_note:
        recipes = [min(recipes, key=lambda recipe: (recipe.prepMinutes + recipe.cookMinutes, recipe.title))]
    else:
        keywords = [word for word in normalized_note.split() if len(word) >= 4]
        matching = [
            recipe
            for recipe in recipes
            if any(keyword in f"{recipe.title} {' '.join(recipe.tags)}".casefold() for keyword in keywords)
        ]
        if matching:
            recipes = matching
    return [
        PlanMeal(
            title=recipe.title,
            description="A deterministic household-friendly replacement using familiar ingredients.",
            ingredients=[ingredient.name for ingredient in recipe.ingredients],
            time={MealType.BREAKFAST: "8:00 AM", MealType.LUNCH: "1:00 PM", MealType.DINNER: "7:30 PM"}[meal_type],
            source_status="replacement_deterministic",
            recipeId=recipe.id,
            ingredientRequirements=recipe.ingredients,
            disclaimer=NUTRITION_ESTIMATE_DISCLAIMER,
        ).model_dump(mode="json")
        for recipe in recipes
    ]
