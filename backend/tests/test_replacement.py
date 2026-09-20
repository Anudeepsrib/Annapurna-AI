from copy import deepcopy
from unittest.mock import patch

from fastapi.testclient import TestClient


def _generate(client: TestClient):
    with patch("app.services.plan_service.llm_service.generate_response", return_value=None):
        response = client.post(
            "/api/v1/generate-plan",
            json={
                "householdSize": "2",
                "spiceLevel": "medium",
                "dietary": "vegetarian",
                "pantryText": "rice - 2 kg\nmoong dal - 1 kg",
            },
        )
    assert response.status_code == 200
    return response.json()["plan"]


def test_locked_meal_blocks_replacement_and_survives_other_replacement(client: TestClient):
    original = _generate(client)
    locked_title = original[0]["meals"]["breakfast"]["title"]

    lock = client.post("/api/v1/plan/Monday/breakfast/lock", json={"locked": True})
    assert lock.status_code == 200
    blocked = client.post("/api/v1/plan/Monday/breakfast/replace", json={})
    assert blocked.status_code == 409

    before = deepcopy(client.get("/api/v1/plan").json())
    replaced = client.post("/api/v1/plan/Thursday/dinner/replace", json={})
    assert replaced.status_code == 200
    result = replaced.json()
    after = result["plan"]

    assert after[0]["meals"]["breakfast"]["title"] == locked_title
    assert after[0]["meals"]["breakfast"]["locked"] is True
    assert after[3]["meals"]["dinner"]["title"] != before[3]["meals"]["dinner"]["title"]
    for day_index, day in enumerate(before):
        for meal_type in ("breakfast", "lunch", "dinner"):
            if (day_index, meal_type) != (3, "dinner"):
                assert after[day_index]["meals"][meal_type] == day["meals"][meal_type]

    assert client.get("/api/v1/grocery-list").json() == result["grocery_optimization"]
