import re
from typing import Any

from pydantic import TypeAdapter, ValidationError

from app.domain.planning.models import CompiledConstraints
from app.models.schemas import DayPlan

VALIDATOR_VERSION = "plan_validator_v2"
_WEEKLY_PLAN_ADAPTER = TypeAdapter(list[DayPlan])
_ALLERGEN_ALIASES = {
    "dairy": ("butter", "cheese", "curd", "dairy", "ghee", "milk", "paneer", "yogurt"),
    "egg": ("egg", "eggs"),
    "gluten": ("barley", "gluten", "rava", "wheat"),
    "peanut": ("groundnut", "peanut", "peanuts"),
    "shellfish": ("crab", "prawn", "shrimp", "shellfish"),
    "tree nut": ("almond", "cashew", "tree nut", "walnut"),
}


class PlanValidator:
    def validate(
        self,
        plan_payload: Any,
        constraints: CompiledConstraints,
    ) -> list[dict[str, Any]]:
        if not isinstance(plan_payload, list) or len(plan_payload) != 7:
            raise ValueError("Plan must contain exactly 7 days")
        try:
            days = _WEEKLY_PLAN_ADAPTER.validate_python(plan_payload)
        except ValidationError as exc:
            raise ValueError("Plan failed schema validation") from exc

        plan = [day.model_dump(mode="json") for day in days]
        text = " ".join(_day_text(day) for day in plan)
        for ingredient in constraints.prohibitedIngredients:
            if _contains(text, ingredient):
                raise ValueError(f"Plan contains prohibited ingredient: {ingredient}")
        for allergen in constraints.allergens:
            terms = _ALLERGEN_ALIASES.get(allergen, (allergen,))
            if any(_contains(text, term) for term in terms):
                raise ValueError(f"Plan contains avoided allergen: {allergen}")
        return plan


def restricted_terms(constraints: CompiledConstraints) -> tuple[str, ...]:
    terms = set(constraints.prohibitedIngredients)
    for allergen in constraints.allergens:
        terms.update(_ALLERGEN_ALIASES.get(allergen, (allergen,)))
    return tuple(sorted(terms))


def _day_text(day: dict[str, Any]) -> str:
    meals = day.get("meals", {})
    return " ".join(_meal_text(meal) for meal in meals.values())


def _meal_text(meal: Any) -> str:
    if not isinstance(meal, dict):
        return ""
    return " ".join(
        (
            str(meal.get("title", "")),
            str(meal.get("description", "")),
            " ".join(str(item) for item in meal.get("ingredients", [])),
        )
    ).casefold()


def _contains(text: str, term: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", text) is not None
