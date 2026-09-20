from functools import lru_cache
from pathlib import Path

from app.domain.recipes.models import MealTypeName, Recipe, RecipeCatalog

DEFAULT_RECIPE_PATH = Path(__file__).parents[2] / "data" / "recipes" / "recipes_v1.json"


@lru_cache(maxsize=4)
def load_recipe_catalog(path: Path = DEFAULT_RECIPE_PATH) -> tuple[Recipe, ...]:
    catalog = RecipeCatalog.model_validate_json(path.read_text(encoding="utf-8"))
    ids = [recipe.id for recipe in catalog.recipes]
    if len(ids) != len(set(ids)):
        raise ValueError("Recipe IDs must be unique")
    return tuple(catalog.recipes)


def recipes_for_meal_type(meal_type: MealTypeName) -> list[Recipe]:
    return [recipe for recipe in load_recipe_catalog() if meal_type in recipe.mealTypes]
