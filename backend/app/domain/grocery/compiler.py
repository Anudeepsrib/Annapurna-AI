import re
from decimal import Decimal
from typing import Any

from app.domain.grocery.models import affinity_for_category
from app.domain.ingredients import (
    IngredientCategory,
    Quantity,
    Unit,
    convert_quantity,
    ingredient_normalizer,
    parse_quantity,
)
from app.models.schemas import ManualShoppingItem, PantryItem

GROCERY_COMPILER_VERSION = "grocery_compiler_v2"

_LEGACY_CATEGORIES = {
    "vegetables": IngredientCategory.PRODUCE,
    "dals": IngredientCategory.DALS_LEGUMES,
    "grains": IngredientCategory.GRAINS,
    "spices": IngredientCategory.SPICES,
    "dairy": IngredientCategory.DAIRY,
    "other": IngredientCategory.OTHER,
}


class GroceryCompiler:
    def compile(
        self,
        plan: list[dict[str, Any]],
        pantry: list[PantryItem],
        manual_items: list[ManualShoppingItem] | None = None,
        exclusions: list[str] | None = None,
        use_soon_requests: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        planned = self._planned_ingredients(plan)
        for manual in manual_items or []:
            key, ingredient_id, category = _ingredient_identity(manual.name, manual.category)
            data = planned.setdefault(key, _ingredient_data(key, ingredient_id, manual.name, category))
            data["manual"] = True
            data["manual_quantity"] = manual.quantity

        excluded_keys = {_ingredient_identity(name)[0] for name in exclusions or []}
        forced_use_soon = {_ingredient_identity(name)[0] for name in use_soon_requests or []}
        pantry_lookup = {
            _ingredient_identity(item.name)[0]: item
            for item in pantry
            if item.name.strip() and _pantry_item_is_usable(item)
        }
        matched_pantry_keys: set[str] = set()
        pantry_first: list[dict[str, Any]] = []
        buy: list[dict[str, Any]] = []

        for key, data in planned.items():
            pantry_item = pantry_lookup.get(key)
            if pantry_item is not None:
                matched_pantry_keys.add(key)
            item = self._reconcile(data, pantry_item, key in forced_use_soon)
            if item["status"] == "need_to_buy":
                if key not in excluded_keys:
                    buy.append(item)
            else:
                pantry_first.append(item)

        self._add_minimum_stock_replenishment(buy, pantry, excluded_keys)
        expiring_unused = self._expiring_unused(
            pantry_lookup,
            matched_pantry_keys,
            forced_use_soon,
        )
        return _sections(pantry_first, buy, expiring_unused)

    def _planned_ingredients(self, plan: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for day in plan:
            for meal in day.get("meals", {}).values():
                if meal.get("leftoverId"):
                    continue
                title = str(meal.get("title", "Unnamed meal"))
                requirements = {
                    _ingredient_identity(str(item.get("name", "")))[0]: item
                    for item in meal.get("ingredientRequirements", [])
                    if isinstance(item, dict) and item.get("name")
                }
                seen: set[str] = set()
                for raw_name in meal.get("ingredients", []):
                    name = " ".join(str(raw_name).split())
                    if not name:
                        continue
                    key, ingredient_id, category = _ingredient_identity(name)
                    self._add_requirement(
                        result.setdefault(key, _ingredient_data(key, ingredient_id, name, category)),
                        title,
                        requirements.get(key),
                    )
                    seen.add(key)
                for key, requirement in requirements.items():
                    if key in seen:
                        continue
                    name = str(requirement["name"])
                    _key, ingredient_id, category = _ingredient_identity(name)
                    self._add_requirement(
                        result.setdefault(key, _ingredient_data(key, ingredient_id, name, category)),
                        title,
                        requirement,
                    )
        return result

    def _add_requirement(self, data: dict[str, Any], title: str, requirement: dict | None) -> None:
        data["count"] += 1
        data["meals"].add(title)
        if not requirement or requirement.get("quantity") is None or not requirement.get("unit"):
            data["unresolved"] = True
            return
        try:
            quantity = Quantity(value=requirement["quantity"], unit=Unit(requirement["unit"]))
            if data["required"] is None:
                data["required"] = quantity
            else:
                converted = convert_quantity(quantity, data["required"].unit)
                data["required"] = Quantity(
                    value=data["required"].value + converted.value,
                    unit=data["required"].unit,
                )
        except (ValueError, TypeError):
            data["unresolved"] = True

    def _reconcile(
        self,
        data: dict[str, Any],
        pantry_item: PantryItem | None,
        forced_use_soon: bool,
    ) -> dict[str, Any]:
        required: Quantity | None = data["required"]
        item = _public_item(data)
        if data["manual"]:
            item["quantity"] = data["manual_quantity"] or "Manual shopping item"
            item["optimization_note"] = "Added manually; pantry subtraction is intentionally not applied."
            return item
        if pantry_item is None:
            item["quantity"] = _format_quantity(required) if required else _unresolved_quantity(data["count"])
            item["requiredQuantity"] = _format_quantity(required)
            return item

        pantry_quantity = _parse_optional_quantity(pantry_item.quantity)
        if required is not None and pantry_quantity is not None:
            try:
                available = convert_quantity(pantry_quantity, required.unit)
                remaining = max(required.value - available.value, Decimal(0))
                item["requiredQuantity"] = _format_quantity(required)
                item["pantryQuantity"] = _format_quantity(available)
                item["buyQuantity"] = _format_quantity(Quantity(value=remaining, unit=required.unit))
                if remaining > 0:
                    item["quantity"] = item["buyQuantity"]
                    item["optimization_note"] = (
                        f"Need {item['requiredQuantity']}; pantry covers {item['pantryQuantity']}."
                    )
                    return item
            except ValueError:
                pass

        item.update(
            {
                "quantity": pantry_item.quantity or _unresolved_quantity(data["count"]),
                "priority": "use_soon" if forced_use_soon or _expires_soon(pantry_item) else "pantry",
                "status": "pantry",
                "optimization_note": _pantry_note(pantry_item, forced_use_soon),
            }
        )
        return item

    def _add_minimum_stock_replenishment(
        self,
        buy: list[dict[str, Any]],
        pantry: list[PantryItem],
        excluded_keys: set[str],
    ) -> None:
        existing = {item["_key"]: item for item in buy}
        for pantry_item in pantry:
            if pantry_item.expired or not pantry_item.minimumStockQuantity:
                continue
            key, ingredient_id, category = _ingredient_identity(pantry_item.name, pantry_item.category)
            if key in excluded_keys:
                continue
            minimum = _parse_optional_quantity(pantry_item.minimumStockQuantity)
            current = _parse_optional_quantity(pantry_item.quantity)
            if minimum is None or current is None:
                continue
            try:
                available = convert_quantity(current, minimum.unit)
            except ValueError:
                continue
            shortage = minimum.value - available.value
            if shortage <= 0:
                continue
            quantity = _format_quantity(Quantity(value=shortage, unit=minimum.unit))
            if key in existing:
                existing[key]["optimization_note"] += f" Also replenish {quantity} to meet minimum stock."
                continue
            data = _ingredient_data(key, ingredient_id, pantry_item.name, category)
            item = _public_item(data)
            item.update(
                {
                    "quantity": quantity,
                    "buyQuantity": quantity,
                    "optimization_note": (
                        f"Pantry is below the configured minimum of {_format_quantity(minimum)}."
                    ),
                }
            )
            buy.append(item)
            existing[key] = item

    def _expiring_unused(
        self,
        pantry_lookup: dict[str, PantryItem],
        matched: set[str],
        forced: set[str],
    ) -> list[dict[str, Any]]:
        items = []
        for key, pantry_item in pantry_lookup.items():
            should_surface = key in forced or (
                key not in matched
                and pantry_item.expiresWithinDays is not None
                and pantry_item.expiresWithinDays <= 5
            )
            if not should_surface:
                continue
            _key, ingredient_id, category = _ingredient_identity(pantry_item.name, pantry_item.category)
            items.append(
                {
                    "_key": key,
                    "id": ingredient_id,
                    "name": pantry_item.name,
                    "quantity": pantry_item.quantity or "Available in pantry",
                    "meals": [],
                    "priority": "use_soon",
                    "status": "pantry_unused",
                    "category": category.value,
                    "storeAffinity": affinity_for_category(category).value,
                    "optimization_note": (
                        "Household command marked this item to use soon."
                        if key in forced
                        else f"Expires within {pantry_item.expiresWithinDays} day(s); plan a side or chutney."
                    ),
                }
            )
        return items


def _ingredient_data(
    key: str,
    ingredient_id: str,
    name: str,
    category: IngredientCategory,
) -> dict[str, Any]:
    return {
        "_key": key,
        "id": ingredient_id,
        "name": name,
        "category": category,
        "count": 0,
        "meals": set(),
        "required": None,
        "unresolved": False,
        "manual": False,
        "manual_quantity": "",
    }


def _public_item(data: dict[str, Any]) -> dict[str, Any]:
    count = data["count"]
    category: IngredientCategory = data["category"]
    return {
        "_key": data["_key"],
        "id": data["id"],
        "name": data["name"],
        "quantity": _unresolved_quantity(count),
        "meals": sorted(data["meals"]),
        "priority": "high" if count >= 3 else "normal",
        "status": "need_to_buy",
        "category": category.value,
        "storeAffinity": affinity_for_category(category).value,
        "requiredQuantity": None,
        "pantryQuantity": None,
        "buyQuantity": None,
        "optimization_note": "Buy or replenish; this ingredient is not in usable pantry stock.",
    }


def _ingredient_identity(
    value: str,
    fallback_category: str = "other",
) -> tuple[str, str, IngredientCategory]:
    match = ingredient_normalizer.normalize(value)
    if match.ingredient is not None:
        return (
            f"ingredient:{match.ingredient.id}",
            match.ingredient.id,
            match.ingredient.category,
        )
    slug = re.sub(r"[^a-z0-9]+", "-", match.normalized_query).strip("-")
    category = _LEGACY_CATEGORIES.get(fallback_category, IngredientCategory.OTHER)
    return f"unresolved:{match.normalized_query}", slug, category


def _pantry_item_is_usable(item: PantryItem) -> bool:
    if item.expired:
        return False
    if not item.quantity:
        return True
    quantity = _parse_optional_quantity(item.quantity)
    return quantity is None or quantity.value > 0


def _parse_optional_quantity(value: str) -> Quantity | None:
    if not value:
        return None
    try:
        return parse_quantity(value)
    except ValueError:
        return None


def _format_quantity(quantity: Quantity | None) -> str | None:
    if quantity is None:
        return None
    return f"{format(quantity.value.normalize(), 'f')} {quantity.unit.value}"


def _unresolved_quantity(count: int) -> str:
    return f"Appears in {count} meal{'s' if count != 1 else ''}; preserve recipe units"


def _expires_soon(item: PantryItem) -> bool:
    return item.expiresWithinDays is not None and item.expiresWithinDays <= 3


def _pantry_note(item: PantryItem, forced: bool) -> str:
    if forced:
        return "Use pantry stock soon as requested by the household."
    if _expires_soon(item):
        return f"Use pantry stock within {item.expiresWithinDays} day(s)."
    return "Use pantry stock before buying more; verify quantity when recipe amounts are unresolved."


def _sections(
    pantry: list[dict[str, Any]],
    buy: list[dict[str, Any]],
    expiring: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sections = []
    for name, items in (
        ("Use From Pantry First", pantry),
        ("Buy / Replenish", buy),
        ("Pantry Items To Use Soon", expiring),
    ):
        if items:
            clean = [{key: value for key, value in item.items() if key != "_key"} for item in items]
            sections.append({"name": name, "items": sorted(clean, key=lambda item: item["name"])})
    return sections
