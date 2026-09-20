from unittest.mock import patch

from fastapi.testclient import TestClient


def _generate_plan(client: TestClient):
    with patch("app.services.plan_service.llm_service.generate_response", return_value=None):
        response = client.post(
            "/api/v1/generate-plan",
            json={
                "householdSize": "2",
                "spiceLevel": "medium",
                "dietary": "vegetarian",
                "pantryText": "spinach - 1 bunch - use within 2 days",
            },
        )
    assert response.status_code == 200


def test_today_records_execution_leftovers_and_feedback(client: TestClient):
    _generate_plan(client)
    response = client.get("/api/v1/today")
    assert response.status_code == 200
    today = response.json()
    assert today["planAvailable"] is True
    assert len(today["meals"]) == 3
    assert today["expiringPantry"][0]["ingredientId"] == "spinach"
    day = today["day"]

    assert client.post(f"/api/v1/today/{day}/breakfast/status", json={"status": "COOKED"}).status_code == 200
    assert client.post(
        f"/api/v1/today/{day}/lunch/status",
        json={"status": "LEFTOVER", "servingsRemaining": 2},
    ).status_code == 200
    for _ in range(2):
        assert client.post(
            f"/api/v1/today/{day}/breakfast/feedback",
            json={"signal": "WOULD_REPEAT"},
        ).status_code == 200

    refreshed = client.get("/api/v1/today").json()
    breakfast = next(meal for meal in refreshed["meals"] if meal["mealType"] == "breakfast")
    assert breakfast["status"] == "COOKED"
    assert breakfast["feedback"] == ["WOULD_REPEAT"]
    assert refreshed["leftovers"][0]["servingsRemaining"] == 2
    assert client.get("/api/v1/leftovers").json()[0]["sourceMealType"] == "lunch"


def test_today_without_a_plan_is_actionable_empty_state(client: TestClient):
    response = client.get("/api/v1/today")
    assert response.status_code == 200
    assert response.json()["planAvailable"] is False
    assert response.json()["meals"] == []
