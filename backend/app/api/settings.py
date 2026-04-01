"""
Settings API routes for local-first configuration.
No authentication required - single user local mode.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings
from app.services.llm_service import llm_service

router = APIRouter()


class LLMSettings(BaseModel):
    provider: str
    base_url: str
    model: str
    api_key: Optional[str] = "not-needed"


class ExternalAPISettings(BaseModel):
    enable_usda: bool
    usda_api_key: Optional[str] = None
    enable_pubmed: bool


class SettingsResponse(BaseModel):
    llm_provider: str
    llm_base_url: str
    llm_model: str
    database_url: str
    enable_usda: bool
    enable_pubmed: bool

    class Config:
        from_attributes = True


@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """
    Get current settings (safe fields only - no sensitive data).
    """
    return SettingsResponse(
        llm_provider=settings.LLM_PROVIDER,
        llm_base_url=settings.LLM_BASE_URL,
        llm_model=settings.LLM_MODEL,
        database_url=settings.DATABASE_URL,
        enable_usda=settings.ENABLE_USDA,
        enable_pubmed=settings.ENABLE_PUBMED,
    )


@router.post("/settings/test-llm")
async def test_llm_connection():
    """
    Test the configured LLM connection.
    """
    result = await llm_service.test_connection()
    if result["status"] == "error":
        raise HTTPException(status_code=503, detail=result)
    return result


@router.get("/settings/models")
async def list_available_models():
    """
    List available models from Ollama (if accessible).
    For other providers, returns configured model info.
    """
    try:
        import httpx

        if settings.LLM_PROVIDER == "ollama":
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.LLM_BASE_URL}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return {"provider": "ollama", "models": models}
                else:
                    return {
                        "provider": "ollama",
                        "models": [],
                        "error": f"Ollama returned status {response.status_code}",
                    }
        else:
            # For other providers, we can't easily list models
            return {
                "provider": settings.LLM_PROVIDER,
                "models": [settings.LLM_MODEL],
                "note": "Model listing only supported for Ollama",
            }
    except Exception as e:
        return {
            "provider": settings.LLM_PROVIDER,
            "models": [],
            "error": str(e),
        }
