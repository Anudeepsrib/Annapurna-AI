import re

from app.core.safety import extract_allergens
from app.domain.planning.models import CompiledConstraints, ConstraintType, PlanningPreferences
from app.models.schemas import PlanRequest

_ANIMAL_INGREDIENTS = (
    "beef",
    "chicken",
    "fish",
    "meat",
    "mutton",
    "pork",
    "prawn",
    "shrimp",
)


class ConstraintEngine:
    def compile(self, request: PlanRequest) -> CompiledConstraints:
        legacy = set(request.teluguAndhraConstraints)
        dietary = request.dietary.casefold()
        types: set[ConstraintType] = set()
        prohibited: set[str] = set()

        if "vegetarian" in legacy or _contains(dietary, "vegetarian"):
            types.add(ConstraintType.VEGETARIAN)
            prohibited.update(_ANIMAL_INGREDIENTS)
        if "no_egg" in legacy or any(
            phrase in dietary for phrase in ("no egg", "egg-free", "eggless", "without egg")
        ):
            types.add(ConstraintType.NO_EGG)
            prohibited.update(("egg", "eggs"))
        if "festival_no_onion_garlic" in legacy or "no onion" in dietary:
            types.add(ConstraintType.NO_ONION)
            prohibited.add("onion")
        if "festival_no_onion_garlic" in legacy or "no garlic" in dietary:
            types.add(ConstraintType.NO_GARLIC)
            prohibited.add("garlic")

        allergens = tuple(extract_allergens(request.dietary, explicit_allergies=request.allergies))
        if allergens:
            types.add(ConstraintType.ALLERGEN)

        return CompiledConstraints(
            types=frozenset(types),
            allergens=allergens,
            prohibitedIngredients=tuple(sorted(prohibited)),
        )

    def compile_preferences(self, request: PlanRequest) -> PlanningPreferences:
        legacy = set(request.teluguAndhraConstraints)
        supplied = request.preferences
        return PlanningPreferences(
            preferredCuisines=(
                supplied.preferredCuisines
                if supplied and supplied.preferredCuisines
                else (["andhra", "telugu"] if "andhra_telugu_style" in legacy else [])
            ),
            spiceLevel=(
                supplied.spiceLevel
                if supplied and supplied.spiceLevel
                else ("mild" if "mild_for_children" in legacy else request.spiceLevel)
            ),
            riceLunchPreference=(
                supplied.riceLunchPreference
                if supplied and supplied.riceLunchPreference is not None
                else "rice_based_lunch" in legacy
            ),
            dalMealsPerWeek=(
                supplied.dalMealsPerWeek
                if supplied and supplied.dalMealsPerWeek is not None
                else (5 if "pappu_or_dal_daily" in legacy else None)
            ),
            fermentedBreakfasts=(
                supplied.fermentedBreakfasts
                if supplied and supplied.fermentedBreakfasts
                else ("okay" if "fermented_breakfasts_ok" in legacy else None)
            ),
            preparationEffort=supplied.preparationEffort if supplied else None,
            weekdayCookingMinutes=supplied.weekdayCookingMinutes if supplied else None,
            leftoversPreference=supplied.leftoversPreference if supplied else None,
            repetitionTolerance=supplied.repetitionTolerance if supplied else "medium",
            pantryUtilizationPreference=(supplied.pantryUtilizationPreference if supplied else "high"),
            ingredientReusePreference=(supplied.ingredientReusePreference if supplied else "medium"),
        )


def _contains(text: str, term: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None
