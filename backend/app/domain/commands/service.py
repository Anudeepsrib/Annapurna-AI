import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CommandValidationError, NotFoundError
from app.domain.commands.models import HouseholdCommandRequest, HouseholdCommandType
from app.domain.feedback import MealType
from app.domain.grocery import GroceryCompiler
from app.domain.ingredients import ingredient_normalizer
from app.domain.pantry import PantryService
from app.domain.planning.replacement import MealReplacementRequest, MealReplacementService
from app.models.schemas import ManualShoppingItem
from app.repositories.plan_repository import PlanRepository

_DAYS = {day.casefold(): day for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")}
_MEALS = "breakfast|lunch|dinner"


class HouseholdCommandService:
    def __init__(self, session: AsyncSession):
        self.plans = PlanRepository(session)
        self.pantry = PantryService(session)
        self.replacements = MealReplacementService(session)
        self.grocery = GroceryCompiler()

    async def execute(self, user_id: str, request: HouseholdCommandRequest) -> dict[str, Any]:
        command = self._parse(request.text)
        if command["type"] == HouseholdCommandType.REPLACE_MEAL:
            result = await self.replacements.replace(
                user_id,
                command["day"],
                MealType(command["mealType"]),
                MealReplacementRequest(note=command.get("note", "")),
            )
            return {"command": command, "result": result}

        saved = await self.plans.get_latest(user_id)
        if saved is None:
            raise NotFoundError("Meal plan")
        payload = saved.plan_data
        if not isinstance(payload, dict):
            payload = {"schema_version": 1, "plan": payload}

        if command["type"] == HouseholdCommandType.EXCLUDE_SHOPPING_ITEM:
            self._append_unique(payload, "shopping_exclusions", command["ingredient"])
        elif command["type"] == HouseholdCommandType.ADD_SHOPPING_ITEM:
            items = payload.setdefault("manual_shopping_items", [])
            if command["ingredient"].casefold() not in {
                str(item.get("name", "")).casefold() for item in items if isinstance(item, dict)
            }:
                items.append(
                    {
                        "name": command["ingredient"],
                        "quantity": command.get("quantity", ""),
                        "category": "other",
                    }
                )
        elif command["type"] == HouseholdCommandType.USE_PANTRY_SOON:
            pantry = await self.pantry.current_legacy_items(user_id)
            wanted = self._ingredient_key(command["ingredient"])
            if not any(self._ingredient_key(item.name) == wanted for item in pantry):
                raise NotFoundError("Pantry item")
            self._append_unique(payload, "use_soon_requests", command["ingredient"])
        else:
            payload.setdefault("household_overrides", {})[command["day"]] = {
                "guestCount": command["guestCount"]
            }
            selected_day = next(
                (day for day in payload.get("plan", []) if day.get("day") == command["day"]),
                None,
            )
            if selected_day is not None:
                selected_day["guestCount"] = command["guestCount"]

        pantry = await self.pantry.current_legacy_items(user_id)
        manual = [
            ManualShoppingItem.model_validate(item)
            for item in payload.get("manual_shopping_items", [])
            if isinstance(item, dict)
        ]
        grocery = self.grocery.compile(
            payload.get("plan", []),
            pantry,
            manual,
            payload.get("shopping_exclusions", []),
            payload.get("use_soon_requests", []),
        )
        payload["grocery_optimization"] = grocery
        payload["schema_version"] = max(int(payload.get("schema_version", 1)), 5)
        await self.plans.update_payload(saved, payload)
        return {"command": command, "result": {"grocery_optimization": grocery}}

    def _parse(self, text: str) -> dict[str, Any]:
        value = " ".join(text.strip().rstrip(".!?").split())
        replace = re.fullmatch(
            rf"replace\s+(\w+)\s+({_MEALS})(?:\s+with\s+(.+))?",
            value,
            re.IGNORECASE,
        )
        easier = re.fullmatch(rf"make\s+(\w+)\s+({_MEALS})\s+easier", value, re.IGNORECASE)
        if replace or easier:
            match = replace or easier
            day = self._day(match.group(1))
            return {
                "type": HouseholdCommandType.REPLACE_MEAL,
                "day": day,
                "mealType": match.group(2).casefold(),
                "note": (match.group(3) if replace and match.lastindex == 3 else "easier") or "",
            }

        exclude = re.fullmatch(r"don['’]?t\s+buy\s+(.+?)(?:\s+this\s+week)?", value, re.IGNORECASE)
        if exclude:
            return {
                "type": HouseholdCommandType.EXCLUDE_SHOPPING_ITEM,
                "ingredient": exclude.group(1),
            }

        use_soon = re.fullmatch(r"use\s+(?:the\s+)?(.+?)\s+tomorrow", value, re.IGNORECASE)
        if use_soon:
            return {"type": HouseholdCommandType.USE_PANTRY_SOON, "ingredient": use_soon.group(1)}

        add_item = re.fullmatch(
            r"add\s+(.+?)(?:\s+-\s+(.+?))?\s+to\s+(?:the\s+)?(?:shopping\s+)?list",
            value,
            re.IGNORECASE,
        )
        if add_item:
            return {
                "type": HouseholdCommandType.ADD_SHOPPING_ITEM,
                "ingredient": add_item.group(1),
                "quantity": add_item.group(2) or "",
            }

        guests = re.fullmatch(
            r"we\s+have\s+(?:(\d+)\s+)?guests?\s+(?:on\s+)?(\w+)",
            value,
            re.IGNORECASE,
        )
        if guests:
            return {
                "type": HouseholdCommandType.ADD_GUESTS,
                "day": self._day(guests.group(2)),
                "guestCount": int(guests.group(1) or 2),
            }
        raise CommandValidationError(
            "Try ‘Use the spinach tomorrow’, ‘We have 2 guests Saturday’, "
            "‘Replace Thursday dinner with paneer’, or ‘Don't buy rice this week’."
        )

    def _day(self, value: str) -> str:
        day = _DAYS.get(value.casefold())
        if day is None:
            raise CommandValidationError("Command must name a weekday")
        return day

    def _append_unique(self, payload: dict, key: str, value: str) -> None:
        values = payload.setdefault(key, [])
        if value.casefold() not in {str(item).casefold() for item in values}:
            values.append(value)

    def _ingredient_key(self, value: str) -> str:
        match = ingredient_normalizer.normalize(value)
        return match.ingredient.id if match.ingredient else match.normalized_query
