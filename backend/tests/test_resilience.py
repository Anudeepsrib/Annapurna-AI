import asyncio
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.services.llm_service import LLMService


def test_request_id_is_returned_on_success_and_domain_errors(client: TestClient):
    request_id = "resilience-test-123"

    success = client.get("/api/v1/health", headers={"X-Request-ID": request_id})
    unknown = client.get("/api/v1/unknown", headers={"X-Request-ID": request_id})
    missing = client.post(
        "/api/v1/plan/Monday/breakfast/replace",
        headers={"X-Request-ID": request_id},
        json={"reason": "use pantry"},
    )

    assert success.headers["X-Request-ID"] == request_id
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "NOT_FOUND"
    assert unknown.json()["error"]["request_id"] == request_id
    assert missing.status_code == 404
    assert missing.headers["X-Request-ID"] == request_id
    assert missing.json()["error"] == {
        "message": "Meal plan not found",
        "code": "NOT_FOUND",
        "request_id": request_id,
    }


def test_invalid_request_has_stable_error_envelope(client: TestClient):
    response = client.post(
        "/api/v1/generate-plan",
        headers={"X-Request-ID": "validation-test"},
        json={"householdSize": "zero"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["request_id"] == "validation-test"


def test_generation_idempotency_replays_result_and_rejects_conflict(client: TestClient):
    headers = {"Idempotency-Key": "plan-request-1"}
    payload = {"householdSize": "2", "spiceLevel": "medium", "dietary": "vegetarian"}

    with patch("app.services.plan_service.llm_service.generate_response", return_value=None) as generate:
        first = client.post("/api/v1/generate-plan", headers=headers, json=payload)
        replay = client.post("/api/v1/generate-plan", headers=headers, json=payload)
        conflict = client.post(
            "/api/v1/generate-plan",
            headers=headers,
            json={**payload, "householdSize": "3"},
        )

    assert first.status_code == 200
    assert replay.status_code == 200
    assert replay.json()["generation_metadata"] == first.json()["generation_metadata"]
    assert generate.call_count == 1
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


def test_llm_retries_then_opens_small_circuit_breaker():
    service = LLMService()
    service.max_retries = 1
    service.failure_threshold = 2
    service.breaker_seconds = 60
    completion = AsyncMock(side_effect=TimeoutError)

    async def scenario():
        with (
            patch("app.services.llm_service.litellm.acompletion", completion),
            patch("app.services.llm_service.asyncio.sleep", AsyncMock()),
        ):
            assert await service.generate_response("system", "user") is None
            assert await service.generate_response("system", "user") is None
            assert completion.await_count == 4
            assert await service.generate_response("system", "user") is None
            assert completion.await_count == 4

    asyncio.run(scenario())
