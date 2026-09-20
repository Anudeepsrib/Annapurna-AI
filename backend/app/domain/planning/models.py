from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ConstraintType(StrEnum):
    VEGETARIAN = "vegetarian"
    NO_EGG = "no_egg"
    ALLERGEN = "allergen"
    NO_ONION = "no_onion"
    NO_GARLIC = "no_garlic"


class CompiledConstraints(BaseModel):
    model_config = ConfigDict(frozen=True)

    types: frozenset[ConstraintType] = frozenset()
    allergens: tuple[str, ...] = ()
    prohibitedIngredients: tuple[str, ...] = ()


class PlanningPreferences(BaseModel):
    preferredCuisines: list[str] = Field(default_factory=list, max_length=8)
    spiceLevel: str | None = Field(default=None, pattern=r"^(mild|medium|spicy)$")
    riceLunchPreference: bool | None = None
    dalMealsPerWeek: int | None = Field(default=None, ge=0, le=21)
    fermentedBreakfasts: str | None = Field(default=None, pattern=r"^(avoid|okay|prefer)$")
    preparationEffort: str | None = Field(default=None, pattern=r"^(low|medium|any)$")
    weekdayCookingMinutes: int | None = Field(default=None, ge=5, le=240)
    leftoversPreference: str | None = Field(default=None, pattern=r"^(avoid|neutral|prefer)$")
    repetitionTolerance: str | None = Field(default=None, pattern=r"^(low|medium|high)$")
    pantryUtilizationPreference: str | None = Field(default=None, pattern=r"^(low|medium|high)$")
    ingredientReusePreference: str | None = Field(default=None, pattern=r"^(low|medium|high)$")


class PlanScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    total: float
    pantryUtilization: float
    expiringItemUtilization: float
    preferenceMatch: float
    variety: float
    ingredientReuse: float
    missingIngredientPenalty: float
    repetitionPenalty: float
    wastePenalty: float


class ScoringWeights(BaseModel):
    model_config = ConfigDict(frozen=True)

    pantryUtilization: float = 2.0
    expiringItemUtilization: float = 3.0
    preferenceMatch: float = 2.0
    variety: float = 1.5
    ingredientReuse: float = 0.5
    missingIngredientPenalty: float = 1.0
    repetitionPenalty: float = 2.0
    wastePenalty: float = 2.0
