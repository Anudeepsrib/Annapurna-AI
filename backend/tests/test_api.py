from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

def test_health_check(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

from app.auth.deps import get_current_user
    
def test_generate_plan_mock(client: TestClient):
    # 1. Override the Auth dependency
    app.dependency_overrides[get_current_user] = lambda: "test_user_123"

    try:
        # Payload
        payload = {
            "householdSize": "2",
            "spiceLevel": "medium",
            "dietary": "vegetarian"
        }
        
        with patch("app.services.plan_service.llm_service.generate_response") as mock_llm:
            mock_llm.return_value = None # Force fallback or return mock JSON
            
            response = client.post("/api/v1/generate-plan", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "plan" in data
            assert len(data["plan"]) > 0
    finally:
        # Clean up override
        app.dependency_overrides.pop(get_current_user, None)
        
def test_get_plan_unauthorized(client: TestClient):
    # Call without auth headers (and without mock override)
    # The dependency_override for DB is active, but Auth is NOT overridden here.
    # Wait, client fixture doesn't override Auth. 
    # BUT, if we run in an env without CLERK_PEM..., it might 500.
    # We should mock get_current_user to RAISE exception or rely on real logic rejection.
    # Real logic checks headers. We send none. Should convert to 401.
    
    # Note: `app.auth.deps.get_current_user` logic:
    # if not authorization: raise 401
    
    response = client.get("/api/v1/plan")
    assert response.status_code == 401
