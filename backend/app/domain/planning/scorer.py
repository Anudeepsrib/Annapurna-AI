from collections import Counter
from typing import Any

from app.domain.ingredients import ingredient_normalizer, parse_quantity
from app.domain.planning.models import (
    PlanningPreferences,
    PlanScore,
    ScoringWeights,
)
from app.models.schemas import PantryItem


class PlanScorer:
    def __init__(self, weights: ScoringWeights | None = None):
        self.weights = weights or ScoringWeights()

    def score(
        self,
        plan: list[dict[str, Any]],
        preferences: PlanningPreferences,
        pantry: list[PantryItem],
    ) -> PlanScore:
        meal_texts, titles, ingredients = _plan_parts(plan)
        ingredient_counts = Counter(_identity(item) for item in ingredients)
        planned = set(ingredient_counts)
        pantry_items = {_identity(item.name): item for item in pantry if _usable(item)}
        pantry_keys = set(pantry_items)
        expiring = {
            key
            for key, item in pantry_items.items()
            if item.expiresWithinDays is not None and item.expiresWithinDays <= 5
        }

        pantry_utilization = _ratio(len(planned & pantry_keys), len(planned))
        expiring_utilization = _ratio(len(planned & expiring), len(expiring), empty=1.0)
        preference_match = _preference_match(plan, meal_texts, preferences)
        variety = _ratio(len(set(titles)), len(titles))
        reused = sum(1 for count in ingredient_counts.values() if count > 1)
        ingredient_reuse = _ratio(reused, len(ingredient_counts))
        missing_penalty = _ratio(len(planned - pantry_keys), len(planned))
        repetition_penalty = 1.0 - variety
        waste_penalty = 1.0 - expiring_utilization

        values = {
            "pantryUtilization": pantry_utilization,
            "expiringItemUtilization": expiring_utilization,
            "preferenceMatch": preference_match,
            "variety": variety,
            "ingredientReuse": ingredient_reuse,
            "missingIngredientPenalty": missing_penalty,
            "repetitionPenalty": repetition_penalty,
            "wastePenalty": waste_penalty,
        }
        positive = (
            self.weights.pantryUtilization
            * _preference_weight(preferences.pantryUtilizationPreference)
            * pantry_utilization
            + self.weights.expiringItemUtilization * expiring_utilization
            + self.weights.preferenceMatch * preference_match
            + self.weights.variety * variety
            + self.weights.ingredientReuse
            * _preference_weight(preferences.ingredientReusePreference)
            * ingredient_reuse
        )
        negative = (
            self.weights.missingIngredientPenalty * missing_penalty
            + self.weights.repetitionPenalty
            * _repetition_weight(preferences.repetitionTolerance)
            * repetition_penalty
            + self.weights.wastePenalty * waste_penalty
        )
        return PlanScore(total=round(positive - negative, 6), **values)

    def select_best(
        self,
        candidates: list[list[dict[str, Any]]],
        preferences: PlanningPreferences,
        pantry: list[PantryItem],
    ) -> list[dict[str, Any]]:
        if not candidates:
            raise ValueError("At least one valid plan candidate is required")
        return max(candidates, key=lambda candidate: self.score(candidate, preferences, pantry).total)


def _plan_parts(plan: list[dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    texts: list[str] = []
    titles: list[str] = []
    ingredients: list[str] = []
    for day in plan:
        for meal in day.get("meals", {}).values():
            title = str(meal.get("title", "")).strip()
            meal_ingredients = [str(item) for item in meal.get("ingredients", [])]
            titles.append(title.casefold())
            ingredients.extend(meal_ingredients)
            texts.append(
                " ".join((title, str(meal.get("description", "")), " ".join(meal_ingredients))).casefold()
            )
    return texts, titles, ingredients


def _preference_match(
    plan: list[dict[str, Any]],
    meal_texts: list[str],
    preferences: PlanningPreferences,
) -> float:
    signals: list[float] = []
    if preferences.preferredCuisines:
        cuisines = [item.casefold() for item in preferences.preferredCuisines]
        matches = sum(any(cuisine in text for cuisine in cuisines) for text in meal_texts)
        signals.append(_ratio(matches, len(meal_texts)))
    if preferences.riceLunchPreference:
        lunches = [str(day.get("meals", {}).get("lunch", {})).casefold() for day in plan]
        signals.append(_ratio(sum("rice" in lunch for lunch in lunches), len(lunches)))
    if preferences.dalMealsPerWeek is not None:
        days_with_dal = sum(
            any(term in str(day).casefold() for term in ("dal", "pappu", "sambar", "sundal", "khichdi", "pesarattu"))
            for day in plan
        )
        target = preferences.dalMealsPerWeek
        signals.append(1.0 if target == 0 and days_with_dal == 0 else min(days_with_dal, target) / max(target, 1))
    if preferences.fermentedBreakfasts in {"avoid", "prefer"}:
        breakfasts = [str(day.get("meals", {}).get("breakfast", {})).casefold() for day in plan]
        fermented = _ratio(sum(any(term in meal for term in ("dosa", "idli", "uttapam")) for meal in breakfasts), 7)
        signals.append(fermented if preferences.fermentedBreakfasts == "prefer" else 1.0 - fermented)
    return sum(signals) / len(signals) if signals else 0.5


def _identity(value: str) -> str:
    match = ingredient_normalizer.normalize(value)
    return match.ingredient.id if match.ingredient else match.normalized_query


def _usable(item: PantryItem) -> bool:
    if item.expired:
        return False
    if not item.quantity:
        return True
    try:
        return parse_quantity(item.quantity).value > 0
    except ValueError:
        return True


def _ratio(numerator: int, denominator: int, *, empty: float = 0.0) -> float:
    return numerator / denominator if denominator else empty


def _preference_weight(value: str | None) -> float:
    return {"low": 0.25, "medium": 0.6, "high": 1.0}.get(value or "medium", 0.6)


def _repetition_weight(value: str | None) -> float:
    return {"low": 1.0, "medium": 0.6, "high": 0.25}.get(value or "medium", 0.6)
