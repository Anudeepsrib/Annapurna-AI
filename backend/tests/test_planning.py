import json
from copy import deepcopy
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domain.planning.constraints import ConstraintEngine
from app.domain.planning.models import ConstraintType, PlanningPreferences
from app.domain.planning.scorer import PlanScorer
from app.domain.planning.validator import PlanValidator
from app.models.schemas import PantryItem, PlanRequest


def _meal(title: str, ingredients: list[str]) -> dict:
    return {
        "title": title,
        "description": "A home-style meal.",
        "ingredients": ingredients,
        "time": "8:00 AM",
        "nutrition": {},
        "confidence": "medium",
        "source_status": "llm_unverified",
        "disclaimer": "Nutrition estimates are approximate.",
    }


def _plan(ingredient: str = "rice", repeated: bool = False) -> list[dict]:
    days = []
    for index, day in enumerate(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")):
        meals = {}
        for meal_type in ("breakfast", "lunch", "dinner"):
            suffix = "same" if repeated else f"{index}-{meal_type}"
            meals[meal_type] = _meal(f"Meal {suffix}", [ingredient])
        days.append(
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
    return days


def test_constraint_engine_compiles_legacy_hard_rules_and_soft_preferences():
    request = PlanRequest(
        dietary="vegetarian, no garlic",
        allergies=["peanuts"],
        teluguAndhraConstraints=[
            "no_egg",
            "festival_no_onion_garlic",
            "rice_based_lunch",
            "pappu_or_dal_daily",
            "mild_for_children",
        ],
        preferences={"dalMealsPerWeek": 3, "repetitionTolerance": "low"},
    )

    engine = ConstraintEngine()
    constraints = engine.compile(request)
    preferences = engine.compile_preferences(request)

    assert constraints.types == {
        ConstraintType.VEGETARIAN,
        ConstraintType.NO_EGG,
        ConstraintType.NO_ONION,
        ConstraintType.NO_GARLIC,
        ConstraintType.ALLERGEN,
    }
    assert constraints.allergens == ("peanut",)
    assert {"chicken", "egg", "onion", "garlic"} <= set(constraints.prohibitedIngredients)
    assert preferences.spiceLevel == "mild"
    assert preferences.riceLunchPreference is True
    assert preferences.dalMealsPerWeek == 3
    assert preferences.repetitionTolerance == "low"


@pytest.mark.parametrize("ingredient", ["chicken", "egg", "onion", "garlic"])
def test_plan_validator_rejects_hard_constraint_violations(ingredient: str):
    request = PlanRequest(
        dietary="vegetarian",
        teluguAndhraConstraints=["vegetarian", "no_egg", "festival_no_onion_garlic"],
    )
    constraints = ConstraintEngine().compile(request)

    with pytest.raises(ValueError, match="prohibited ingredient"):
        PlanValidator().validate(_plan(ingredient), constraints)


def test_plan_validator_uses_word_boundaries_and_keeps_soft_preferences_soft():
    request = PlanRequest(
        dietary="vegetarian",
        teluguAndhraConstraints=["vegetarian", "no_egg", "rice_based_lunch", "pappu_or_dal_daily"],
    )
    constraints = ConstraintEngine().compile(request)

    validated = PlanValidator().validate(_plan("eggplant"), constraints)

    assert len(validated) == 7


def test_plan_scorer_prefers_variety_and_expiring_pantry_use():
    pantry = [
        PantryItem(name="spinach", quantity="1 bunch", expiresWithinDays=2),
        PantryItem(name="rice", quantity="2 kg", expiresWithinDays=90),
    ]
    preferred = _plan("spinach")
    missing_and_repeated = _plan("wheat", repeated=True)
    preferences = PlanningPreferences(pantryUtilizationPreference="high", repetitionTolerance="low")
    scorer = PlanScorer()

    assert scorer.score(preferred, preferences, pantry).total > scorer.score(
        missing_and_repeated,
        preferences,
        pantry,
    ).total
    assert scorer.select_best([missing_and_repeated, preferred], preferences, pantry) is preferred


def test_vegetarian_api_rejects_chicken_candidate(client: TestClient):
    candidate = _plan("rice")
    invalid = deepcopy(candidate)
    invalid[0]["meals"]["dinner"] = _meal("Chicken curry", ["chicken", "spices"])

    with patch("app.services.plan_service.llm_service.generate_response", return_value=json.dumps({"plan": invalid})):
        response = client.post(
            "/api/v1/generate-plan",
            json={"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["source_status"] == "fallback_invalid_llm_json"
    assert "chicken" not in json.dumps(data["plan"]).casefold()


def test_dairy_allergy_guardrail_fallback_avoids_dairy_aliases(client: TestClient):
    response = client.post(
        "/api/v1/generate-plan",
        json={
            "householdSize": "2",
            "spiceLevel": "medium",
            "dietary": "vegetarian with dairy allergy",
            "allergies": ["dairy"],
        },
    )

    assert response.status_code == 200
    serialized = json.dumps(response.json()["plan"]).casefold()
    assert all(term not in serialized for term in ("milk", "curd", "ghee", "paneer", "yogurt"))
