from enum import StrEnum
from typing import Protocol

from app.domain.ingredients import IngredientCategory


class StoreAffinity(StrEnum):
    INDIAN_GROCERY = "indian_grocery"
    BULK = "bulk"
    GENERAL_SUPERMARKET = "general_supermarket"


class RetailerAdapter(Protocol):
    """Optional fulfillment boundary; planning never depends on an adapter."""

    async def search_product(self, ingredient_id: str, query: str) -> list[dict]: ...

    async def get_price(self, product_id: str) -> str | None: ...

    async def get_availability(self, product_id: str) -> bool | None: ...


def affinity_for_category(category: IngredientCategory) -> StoreAffinity:
    if category in {IngredientCategory.DALS_LEGUMES, IngredientCategory.SPICES}:
        return StoreAffinity.INDIAN_GROCERY
    if category in {IngredientCategory.GRAINS, IngredientCategory.HOUSEHOLD_STAPLES}:
        return StoreAffinity.BULK
    return StoreAffinity.GENERAL_SUPERMARKET
