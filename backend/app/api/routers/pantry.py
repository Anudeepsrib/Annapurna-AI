from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.pantry import PantryImportRequest, PantryService, PantryTransactionRequest

router = APIRouter(prefix="/pantry", tags=["pantry"])


@router.get("")
async def get_pantry(session: AsyncSession = Depends(get_session)):
    return await PantryService(session).list_items("local-user")


@router.post("/import")
async def import_pantry(
    request: PantryImportRequest,
    session: AsyncSession = Depends(get_session),
):
    return await PantryService(session).import_text("local-user", request.pantryText)


@router.post("/{item_id}/transactions")
async def record_pantry_transaction(
    item_id: int,
    request: PantryTransactionRequest,
    session: AsyncSession = Depends(get_session),
):
    item, transaction = await PantryService(session).record_transaction("local-user", item_id, request)
    return {"item": item, "transaction": transaction}


@router.get("/{item_id}/transactions")
async def get_pantry_transactions(
    item_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await PantryService(session).list_transactions("local-user", item_id)
