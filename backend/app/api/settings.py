from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import is_local_llm_base_url, settings
from app.services.llm_service import llm_service

router = APIRouter()


class SettingsResponse(BaseModel):
    app_env: str
    debug: bool
    llm_provider: str
    llm_base_url: str
    llm_model: str
    llm_network_mode: str
    llm_privacy_note: str
    database_url: str
    enable_external_network: bool
    enable_usda: bool
    enable_pubmed: bool


@router.get("/", response_model=SettingsResponse)
async def get_settings():
    """
    Get current settings (safe fields only - no sensitive data).
    """
    return SettingsResponse(
        app_env=settings.APP_ENV,
        debug=settings.DEBUG,
        llm_provider=settings.LLM_PROVIDER,
        llm_base_url=settings.LLM_BASE_URL,
        llm_model=settings.LLM_MODEL,
        llm_network_mode="local" if is_local_llm_base_url(settings.LLM_BASE_URL) else "external",
        llm_privacy_note=(
            "Local model endpoint; prompts stay on this machine by default."
            if is_local_llm_base_url(settings.LLM_BASE_URL)
            else "External model endpoint; family profile, pantry, and dietary prompts may leave this machine."
        ),
        database_url=settings.DATABASE_URL,
        enable_external_network=settings.ENABLE_EXTERNAL_NETWORK,
        enable_usda=settings.ENABLE_USDA,
        enable_pubmed=settings.ENABLE_PUBMED,
    )


@router.post("/test-llm")
async def test_llm_connection():
    """
    Test the configured LLM connection.
    """
    result = await llm_service.test_connection()
    if result["status"] == "error":
        raise HTTPException(status_code=503, detail=result)
    return result


@router.get("/models")
async def list_available_models():
    """
    List available models from Ollama (if accessible).
    For other providers, returns configured model info.
    """
    try:
        import httpx

        if settings.LLM_PROVIDER == "ollama":
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.LLM_BASE_URL}/api/tags", timeout=10)
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
    except Exception:
        return {
            "provider": settings.LLM_PROVIDER,
            "models": [],
            "error": "Could not reach local model endpoint. Is Ollama running?",
        }
