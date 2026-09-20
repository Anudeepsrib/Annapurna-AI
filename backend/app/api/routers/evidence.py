from fastapi import APIRouter

from app.models.schemas import EvidenceResponse
from app.services.evidence_service import evidence_service
from app.services.orchestrator import orchestrator
from app.services.usda_client import usda_client

router = APIRouter(tags=["evidence"])


@router.get("/evidence/{topic}", response_model=EvidenceResponse)
async def get_evidence(topic: str):
    return await orchestrator.get_evidence(topic)


@router.get("/mcp/ifct/search")
async def search_ifct(query: str):
    return {"results": evidence_service.get_ifct_food(query)}


@router.get("/mcp/usda/search")
async def search_usda(query: str):
    return await usda_client.search_foods(query)
