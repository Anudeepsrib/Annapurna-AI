import re
from typing import Any

from app.domain.ingredients import ingredient_normalizer, parse_quantity
from app.models.schemas import PantryItem

GROCERY_COMPILER_VERSION = "grocery_compiler_v1"


class GroceryCompiler:
    def compile(
        self,
        plan: list[dict[str, Any]],
        pantry: list[PantryItem],
    ) -> list[dict[str, Any]]:
        ingredients_map: dict[str, dict[str, Any]] = {}

        for day in plan:
            for meal_info in day.get("meals", {}).values():
                meal_title = meal_info.get("title", "Unnamed meal")
                for raw_ingredient in meal_info.get("ingredients", []):
                    ingredient_name = " ".join(str(raw_ingredient).split())
                    if not ingredient_name:
                        continue
                    key, ingredient_id = _ingredient_identity(ingredient_name)
                    if key not in ingredients_map:
                        ingredients_map[key] = {
                            "id": ingredient_id,
                            "name": ingredient_name,
                            "count": 0,
                            "meals": set(),
                        }
                    ingredients_map[key]["count"] += 1
                    ingredients_map[key]["meals"].add(meal_title)

        pantry_lookup = {
            _ingredient_identity(item.name)[0]: item
            for item in pantry
            if item.name.strip() and _pantry_item_is_usable(item)
        }
        matched_pantry_keys: set[str] = set()
        pantry_first_items = []
        buy_items = []

        for data in ingredients_map.values():
            count = data["count"]
            pantry_match = _find_pantry_match(data["name"], pantry_lookup)
            item = {
                "id": data["id"],
                "name": data["name"],
                "quantity": f"Appears in {count} meal{'s' if count != 1 else ''}; preserve recipe units",
                "meals": sorted(data["meals"]),
                "priority": "high" if count >= 3 else "normal",
                "status": "need_to_buy",
                "optimization_note": "Buy or replenish; this ingredient is not in the provided pantry.",
            }

            if pantry_match is not None:
                pantry_key, pantry_item = pantry_match
                matched_pantry_keys.add(pantry_key)
                expires_note = ""
                priority = "pantry"
                if pantry_item.expiresWithinDays is not None and pantry_item.expiresWithinDays <= 3:
                    priority = "use_soon"
                    expires_note = f" Use within {pantry_item.expiresWithinDays} day(s)."
                item.update(
                    {
                        "quantity": pantry_item.quantity or item["quantity"],
                        "priority": priority,
                        "status": "pantry",
                        "optimization_note": f"Use pantry stock before buying more.{expires_note}",
                    }
                )
                pantry_first_items.append(item)
            else:
                buy_items.append(item)

        expiring_unused_items = []
        for key, pantry_item in pantry_lookup.items():
            if key in matched_pantry_keys or pantry_item.expiresWithinDays is None or pantry_item.expiresWithinDays > 5:
                continue
            expiring_unused_items.append(
                {
                    "id": f"pantry-{re.sub(r'[^a-z0-9]+', '-', key).strip('-')}",
                    "name": pantry_item.name,
                    "quantity": pantry_item.quantity or "Available in pantry",
                    "meals": [],
                    "priority": "use_soon",
                    "status": "pantry_unused",
                    "optimization_note": (
                        f"Pantry item expires within {pantry_item.expiresWithinDays} day(s); "
                        "consider a chutney, podi, stir-fry, or side dish."
                    ),
                }
            )

        categories = []
        if pantry_first_items:
            categories.append(
                {
                    "name": "Use From Pantry First",
                    "items": sorted(pantry_first_items, key=lambda item: item["name"]),
                }
            )
        if buy_items:
            categories.append(
                {
                    "name": "Buy / Replenish",
                    "items": sorted(buy_items, key=lambda item: (item["priority"] != "high", item["name"])),
                }
            )
        if expiring_unused_items:
            categories.append(
                {
                    "name": "Pantry Items To Use Soon",
                    "items": sorted(expiring_unused_items, key=lambda item: item["name"]),
                }
            )
        return categories


def _ingredient_identity(value: str) -> tuple[str, str]:
    match = ingredient_normalizer.normalize(value)
    if match.ingredient is not None:
        return f"ingredient:{match.ingredient.id}", match.ingredient.id
    slug = re.sub(r"[^a-z0-9]+", "-", match.normalized_query).strip("-")
    return f"unresolved:{match.normalized_query}", slug


def _pantry_item_is_usable(item: PantryItem) -> bool:
    if item.expired:
        return False
    if not item.quantity:
        return True
    try:
        return parse_quantity(item.quantity).value > 0
    except ValueError:
        return True


def _find_pantry_match(
    ingredient_name: str,
    pantry_lookup: dict[str, PantryItem],
) -> tuple[str, PantryItem] | None:
    ingredient_key = _ingredient_identity(ingredient_name)[0]
    if ingredient_key in pantry_lookup:
        return ingredient_key, pantry_lookup[ingredient_key]
    return None
