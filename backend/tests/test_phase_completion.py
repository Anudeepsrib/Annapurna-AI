import json
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domain.grocery import GroceryCompiler
from app.domain.planning.models import PlanningPreferences
from app.domain.planning.scorer import PlanScorer
from app.domain.recipes import load_recipe_catalog
from app.models.schemas import ManualShoppingItem, PantryItem
from app.services.plan_service import llm_service


def _meal(title: str, ingredient: str = "rice") -> dict:
    return {
        "title": title,
        "description": "Home-style meal",
        "ingredients": [ingredient],
        "time": "8:00 AM",
        "nutrition": {},
        "confidence": "medium",
        "source_status": "test",
        "disclaimer": "General wellness only.",
    }


def _plan(first_title: str) -> list[dict]:
    days = []
    for index, day in enumerate(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")):
        days.append(
            {
                "day": day,
                "date": f"Day {index + 1}",
                "meals": {
                    "breakfast": _meal(first_title if index == 0 else f"Breakfast {index}"),
                    "lunch": _meal(f"Lunch {index}"),
                    "dinner": _meal(f"Dinner {index}"),
                },
                "confidence": "medium",
                "source_status": "test",
                "disclaimer": "General wellness only.",
                "safety_notes": [],
            }
        )
    return days


def _generate(client: TestClient, **overrides) -> dict:
    payload = {
        "householdSize": "2",
        "spiceLevel": "medium",
        "dietary": "vegetarian",
        **overrides,
    }
    with patch("app.services.plan_service.llm_service.generate_response", return_value=None):
        response = client.post("/api/v1/generate-plan", json=payload)
    assert response.status_code == 200
    return response.json()


def test_recipe_catalog_has_structured_quantities_for_replacements():
    recipes = load_recipe_catalog()

    assert len(recipes) >= 10
    paneer = next(recipe for recipe in recipes if recipe.id == "paneer_bhurji_roti")
    assert paneer.ingredients[0].quantity is not None
    assert paneer.ingredients[0].unit.value == "g"
    assert paneer.instructions


def test_grocery_compiler_reconciles_quantities_minimum_stock_and_manual_items():
    plan = _plan("Rice meal")
    plan[0]["meals"]["breakfast"]["ingredientRequirements"] = [
        {"ingredientId": "rice", "name": "rice", "quantity": "2500", "unit": "g"}
    ]
    pantry = [
        PantryItem(
            name="rice",
            quantity="2 kg",
            category="grains",
            minimumStockQuantity="3 kg",
        )
    ]

    grocery = GroceryCompiler().compile(
        plan,
        pantry,
        [ManualShoppingItem(name="dish soap", quantity="1 bottle", category="household_staples")],
    )
    buy = next(section for section in grocery if section["name"] == "Buy / Replenish")["items"]
    rice = next(item for item in buy if item["id"] == "rice")

    assert rice["requiredQuantity"] == "2500 g"
    assert rice["pantryQuantity"] == "2000 g"
    assert rice["buyQuantity"] == "500 g"
    assert "minimum stock" in rice["optimization_note"]
    assert next(item for item in buy if item["name"] == "dish soap")["storeAffinity"] == "general_supermarket"


def test_feedback_weights_change_candidate_ranking():
    preferred = _plan("Family favorite")
    neutral = deepcopy(preferred)
    neutral[0]["meals"]["breakfast"]["title"] = "Unknown meal"
    scorer = PlanScorer()

    selected = scorer.select_best(
        [neutral, preferred],
        PlanningPreferences(),
        [],
        {"family favorite": 2.0},
    )

    assert selected is preferred


def test_recorded_feedback_influences_the_next_generated_plan(client: TestClient):
    _generate(client)
    today = client.get("/api/v1/today").json()
    favorite = today["meals"][0]["meal"]["title"]
    assert client.post(
        f"/api/v1/today/{today['day']}/breakfast/feedback",
        json={"signal": "WOULD_REPEAT"},
    ).status_code == 200
    preferred = _plan(favorite)
    neutral = _plan("Unseen breakfast")

    with patch(
        "app.services.plan_service.llm_service.generate_response",
        return_value=json.dumps({"candidates": [{"plan": neutral}, {"plan": preferred}]}),
    ):
        response = client.post(
            "/api/v1/generate-plan",
            json={"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian"},
        )

    assert response.status_code == 200
    assert response.json()["plan"][0]["meals"]["breakfast"]["title"] == favorite


def test_locked_meal_survives_full_and_day_regeneration(client: TestClient):
    first = _generate(client)
    title = first["plan"][0]["meals"]["breakfast"]["title"]
    assert client.post("/api/v1/plan/Monday/breakfast/lock", json={"locked": True}).status_code == 200

    regenerated = _generate(client, householdSize="3")
    assert regenerated["plan"][0]["meals"]["breakfast"]["title"] == title
    assert regenerated["plan"][0]["meals"]["breakfast"]["locked"] is True

    day = client.post("/api/v1/plan/Monday/regenerate")
    assert day.status_code == 200
    assert "breakfast" not in day.json()["changed"]
    assert day.json()["plan"][0]["meals"]["breakfast"]["title"] == title


def test_leftovers_are_editable_reusable_and_ate_out_is_recorded(client: TestClient):
    _generate(client)
    today = client.get("/api/v1/today").json()
    day = today["day"]
    usable_until = (datetime.now(UTC) + timedelta(days=3)).isoformat()
    assert client.post(
        f"/api/v1/today/{day}/lunch/status",
        json={"status": "LEFTOVER", "servingsRemaining": 3, "usableUntil": usable_until},
    ).status_code == 200
    assert client.post(f"/api/v1/today/{day}/dinner/status", json={"status": "ATE_OUT"}).status_code == 200

    leftover = client.get("/api/v1/leftovers").json()[0]
    updated = client.patch(f"/api/v1/leftovers/{leftover['id']}", json={"servingsRemaining": 1})
    assert updated.json()["servingsRemaining"] == 1
    assigned = client.post(f"/api/v1/leftovers/{leftover['id']}/use/Tuesday/dinner")
    assert assigned.status_code == 200
    assert assigned.json()["leftoverId"] == leftover["id"]
    assert client.patch(f"/api/v1/leftovers/{leftover['id']}", json={"consumed": True}).status_code == 200
    assert client.get("/api/v1/leftovers").json() == []


def test_household_commands_compile_then_mutate_validated_state(client: TestClient):
    _generate(client, pantryText="spinach - 1 bunch")

    use_soon = client.post("/api/v1/commands", json={"text": "Use the spinach tomorrow."})
    assert use_soon.status_code == 200
    assert use_soon.json()["command"]["type"] == "USE_PANTRY_SOON"
    grocery = client.get("/api/v1/grocery-list").json()
    surfaced = [item for section in grocery for item in section["items"] if item["id"] == "spinach"]
    assert any(item["priority"] == "use_soon" for item in surfaced)

    excluded = client.post("/api/v1/commands", json={"text": "Don't buy rice this week."})
    assert excluded.status_code == 200
    buy = next(section for section in client.get("/api/v1/grocery-list").json() if section["name"] == "Buy / Replenish")
    assert all(item["id"] != "rice" for item in buy["items"])

    guests = client.post("/api/v1/commands", json={"text": "We have 3 guests Saturday."})
    assert guests.json()["command"] == {"type": "ADD_GUESTS", "day": "Saturday", "guestCount": 3}

    manual = client.post("/api/v1/commands", json={"text": "Add dish soap - 1 bottle to the shopping list."})
    assert manual.status_code == 200
    grocery = client.get("/api/v1/grocery-list").json()
    assert any(item["name"] == "dish soap" for section in grocery for item in section["items"])

    replacement = client.post("/api/v1/commands", json={"text": "Replace Thursday dinner with paneer."})
    assert replacement.status_code == 200
    assert "Paneer" in replacement.json()["result"]["meal"]["title"]

    unsupported = client.post("/api/v1/commands", json={"text": "Do something magical"})
    assert unsupported.status_code == 422
    assert unsupported.json()["error"]["code"] == "COMMAND_UNSUPPORTED"


def test_timeout_metadata_and_unresolved_pantry_error_codes(client: TestClient):
    async def timeout(*_args, **_kwargs):
        llm_service.last_failure_code = "LLM_TIMEOUT"
        return None

    with patch("app.services.plan_service.llm_service.generate_response", side_effect=timeout):
        response = client.post(
            "/api/v1/generate-plan",
            json={"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian"},
        )
    assert response.json()["source_status"] == "fallback_llm_timeout"
    assert response.json()["generation_metadata"]["error_code"] == "LLM_TIMEOUT"

    unresolved = client.post("/api/v1/pantry/import", json={"pantryText": "mystery leaf - some"}).json()[0]
    consume = client.post(
        f"/api/v1/pantry/{unresolved['id']}/transactions",
        json={
            "transactionType": "CONSUME",
            "quantity": "1",
            "unit": "piece",
            "expectedVersion": unresolved["version"],
        },
    )
    assert consume.status_code == 422
    assert consume.json()["error"]["code"] == "PANTRY_ITEM_UNRESOLVED"
