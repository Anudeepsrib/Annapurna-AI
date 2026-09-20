from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.ingredients import Unit

MealTypeName = Literal["breakfast", "lunch", "dinner"]


class RecipeIngredient(BaseModel):
    model_config = ConfigDict(frozen=True)

    ingredientId: str | None = None
    name: str = Field(min_length=1, max_length=120)
    quantity: Decimal | None = Field(default=None, gt=0)
    unit: Unit | None = None
    optional: bool = False
    preparation: str = Field(default="", max_length=120)

    @model_validator(mode="after")
    def quantity_and_unit_move_together(self) -> "RecipeIngredient":
        if (self.quantity is None) != (self.unit is None):
            raise ValueError("recipe ingredient quantity and unit must be supplied together")
        return self


class Recipe(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^[a-z0-9_]+$")
    title: str = Field(min_length=1, max_length=140)
    cuisine: str
    region: str
    mealTypes: list[MealTypeName] = Field(min_length=1)
    ingredients: list[RecipeIngredient] = Field(min_length=1)
    instructions: list[str] = Field(min_length=1)
    prepMinutes: int = Field(ge=0, le=240)
    cookMinutes: int = Field(ge=0, le=360)
    difficulty: Literal["easy", "medium", "advanced"]
    spiceLevel: Literal["mild", "medium", "spicy"]
    tags: list[str] = Field(default_factory=list)


class RecipeCatalog(BaseModel):
    schemaVersion: Literal[1]
    recipes: list[Recipe]
