import asyncio
import json
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.domain.planning.grocery import GroceryCompiler
from app.domain.planning.models import PlanningPreferences
from app.domain.planning.planner import CandidatePlanner
from app.models.schemas import PantryItem, PlanRequest


def _meal(title: str, ingredient: str) -> dict:
    return {
        "title": title,
        "description": "A home-style vegetarian meal.",
        "ingredients": [ingredient],
        "time": "8:00 AM",
        "nutrition": {},
        "confidence": "medium",
        "source_status": "llm_unverified",
        "disclaimer": "Nutrition estimates are approximate.",
    }


def _plan(ingredient: str, *, repeated: bool = False) -> list[dict]:
    result = []
    for index, day in enumerate(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")):
        meals = {
            meal_type: _meal(
                "Repeated meal" if repeated else f"{ingredient.title()} {day} {meal_type}",
                ingredient,
            )
            for meal_type in ("breakfast", "lunch", "dinner")
        }
        result.append(
            {
                "day": day,
                "date": f"Day {index + 1}",
                "meals": meals,
                "confidence": "medium",
                "source_status": "llm_unverified",
                "disclaimer": "General wellness only.",
                "safety_notes": [],
            }
        )
    return result


def test_candidate_planner_extracts_multiple_fenced_candidates():
    response = f"```json\n{json.dumps({'candidates': [{'plan': _plan('rice')}, {'plan': _plan('spinach')} ]})}\n```"
    llm = AsyncMock()
    llm.generate_response.return_value = response
    planner = CandidatePlanner(llm)

    candidates = asyncio.run(
        planner.generate_candidates(
            PlanRequest(),
            PlanningPreferences(),
            "local-user",
        )
    )

    assert candidates is not None
    assert len(candidates) == 2
    assert candidates[1][0]["meals"]["breakfast"]["ingredients"] == ["spinach"]


def test_plan_service_ranks_multiple_valid_candidates(client: TestClient):
    payload = {
        "candidates": [
            {"plan": _plan("wheat", repeated=True)},
            {"plan": _plan("spinach")},
        ]
    }
    request = {
        "householdSize": "2",
        "spiceLevel": "medium",
        "dietary": "vegetarian",
        "pantryInventory": [
            {"name": "spinach", "quantity": "1 bunch", "category": "vegetables", "expiresWithinDays": 2}
        ],
    }

    with patch("app.services.plan_service.llm_service.generate_response", return_value=json.dumps(payload)):
        response = client.post("/api/v1/generate-plan", json=request)

    assert response.status_code == 200
    data = response.json()
    assert data["source_status"] == "llm_schema_validated"
    assert data["plan"][0]["meals"]["breakfast"]["ingredients"] == ["spinach"]
    assert data["generation_metadata"]["planner_version"] == "candidate_planner_v2"


def test_extracted_grocery_compiler_keeps_canonical_alias_matching():
    categories = GroceryCompiler().compile(
        _plan("kandi pappu"),
        [PantryItem(name="toor dal", quantity="1 kg", category="dals")],
    )

    pantry_items = next(category for category in categories if category["name"] == "Use From Pantry First")["items"]
    assert len(pantry_items) == 1
    assert pantry_items[0]["id"] == "pigeon_pea"
    assert pantry_items[0]["status"] == "pantry"
