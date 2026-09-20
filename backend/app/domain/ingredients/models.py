from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.ingredients.units import Unit


class IngredientCategory(StrEnum):
    PRODUCE = "produce"
    DAIRY = "dairy"
    GRAINS = "grains"
    DALS_LEGUMES = "dals_legumes"
    SPICES = "spices"
    FROZEN = "frozen"
    PACKAGED_FOODS = "packaged_foods"
    HOUSEHOLD_STAPLES = "household_staples"
    OTHER = "other"


class StorageLocation(StrEnum):
    PANTRY = "pantry"
    REFRIGERATOR = "refrigerator"
    FREEZER = "freezer"


class MatchType(StrEnum):
    CANONICAL = "canonical"
    ALIAS = "alias"
    NORMALIZED_TOKEN = "normalized_token"
    FUZZY = "fuzzy"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class Ingredient(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^[a-z0-9_]+$")
    canonical_name: str = Field(pattern=r"^[a-z0-9_]+$")
    display_name: str
    aliases: list[str] = Field(default_factory=list)
    regional_names: dict[str, str] = Field(default_factory=dict)
    category: IngredientCategory
    default_unit: Unit
    storage_location: StorageLocation
    vegetarian: bool = True
    allergens: list[str] = Field(default_factory=list)
    approximate_shelf_life_days: int | None = Field(default=None, ge=0)


class IngredientOntology(BaseModel):
    schema_version: Literal[1]
    ingredients: list[Ingredient]


class IngredientMatch(BaseModel):
    model_config = ConfigDict(frozen=True)

    query: str
    normalized_query: str
    match_type: MatchType
    ingredient: Ingredient | None = None
