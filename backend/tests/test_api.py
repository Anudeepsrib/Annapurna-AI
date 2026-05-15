import asyncio
import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.pubmed_client import pubmed_client
from app.services.usda_client import usda_client


def test_health_check_does_not_leak_secrets(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    serialized = json.dumps(data).lower()
    assert "api_key" not in serialized
    assert "database_url" not in serialized


def test_settings_defaults_are_local_first(client: TestClient):
    response = client.get("/api/v1/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["enable_external_network"] is False
    assert data["enable_usda"] is False
    assert data["enable_pubmed"] is False
    assert data["llm_provider"] == "ollama"


def test_optional_fetchers_do_not_call_network_by_default():
    assert settings.ENABLE_EXTERNAL_NETWORK is False
    assert settings.ENABLE_USDA is False
    assert settings.ENABLE_PUBMED is False

    async def run_checks():
        with patch("app.services.usda_client.httpx.AsyncClient") as usda_client_mock:
            assert await usda_client.search_foods("rice") == {}
            usda_client_mock.assert_not_called()

        with patch("app.services.pubmed_client.httpx.AsyncClient") as pubmed_client_mock:
            assert await pubmed_client.search("protein") == []
            assert await pubmed_client.fetch_details(["1"]) == []
            pubmed_client_mock.assert_not_called()

    asyncio.run(run_checks())


def test_generate_plan_returns_clear_error_when_llm_unavailable(client: TestClient):
    payload = {"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian"}

    with patch("app.services.plan_service.llm_service.generate_response", return_value=None):
        response = client.post("/api/v1/generate-plan", json=payload)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "LLMUnavailableError"


def test_malformed_llm_json_falls_back_to_valid_plan(client: TestClient):
    payload = {"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian"}

    with patch("app.services.plan_service.llm_service.generate_response", return_value="not json"):
        response = client.post("/api/v1/generate-plan", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["source_status"] == "fallback_invalid_llm_json"
    assert len(data["plan"]) == 7
    assert data["plan"][0]["meals"]["breakfast"]["title"]
    assert "approximate" in data["plan"][0]["meals"]["breakfast"]["disclaimer"].lower()


def test_missing_llm_fields_fall_back_to_valid_plan(client: TestClient):
    incomplete_plan = {"plan": [{"day": "Monday"} for _ in range(7)]}
    payload = {"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian"}

    with patch("app.services.plan_service.llm_service.generate_response", return_value=json.dumps(incomplete_plan)):
        response = client.post("/api/v1/generate-plan", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["source_status"] == "fallback_invalid_llm_json"
    assert len(data["plan"]) == 7


def test_diabetes_prompt_returns_wellness_guardrail(client: TestClient):
    response = client.post(
        "/api/v1/generate-plan",
        json={"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian with diabetes"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["source_status"] == "safety_guardrail"
    assert any("registered dietitian" in note.lower() for note in data["safety_notes"])


def test_kidney_disease_prompt_returns_wellness_guardrail(client: TestClient):
    response = client.post(
        "/api/v1/generate-plan",
        json={"householdSize": "2", "spiceLevel": "mild", "dietary": "kidney disease low potassium"},
    )

    assert response.status_code == 200
    assert response.json()["source_status"] == "safety_guardrail"


def test_allergy_prompt_returns_guardrail_and_avoids_allergen(client: TestClient):
    response = client.post(
        "/api/v1/generate-plan",
        json={
            "householdSize": "2",
            "spiceLevel": "medium",
            "dietary": "vegetarian and allergic to peanuts",
            "allergies": ["peanut"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["source_status"] == "safety_guardrail"
    assert "peanut" not in json.dumps(data["plan"]).lower()


def test_eating_disorder_extreme_weight_loss_prompt_returns_guardrail(client: TestClient):
    response = client.post(
        "/api/v1/generate-plan",
        json={"householdSize": "1", "spiceLevel": "mild", "dietary": "800 calories extreme weight loss"},
    )

    assert response.status_code == 200
    assert response.json()["source_status"] == "safety_guardrail"


def test_pregnancy_prompt_returns_wellness_guardrail(client: TestClient):
    response = client.post(
        "/api/v1/generate-plan",
        json={"householdSize": "2", "spiceLevel": "medium", "dietary": "pregnancy vegetarian meals"},
    )

    assert response.status_code == 200
    assert response.json()["source_status"] == "safety_guardrail"
