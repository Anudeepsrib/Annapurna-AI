import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.db import GenerationRequestRecord, MealPlan
from app.models.schemas import GenerationMetadata


class PlanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(
        self,
        user_id: str,
        payload: dict[str, Any],
        metadata: GenerationMetadata,
    ) -> MealPlan:
        plan = MealPlan(
            user_id=user_id,
            plan_json=json.dumps(payload),
            generation_metadata_json=metadata.model_dump_json(),
        )
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_latest(self, user_id: str) -> MealPlan | None:
        statement = select(MealPlan).where(MealPlan.user_id == user_id).order_by(MealPlan.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def update_payload(self, plan: MealPlan, payload: dict[str, Any]) -> MealPlan:
        plan.plan_json = json.dumps(payload)
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_generation_request(
        self,
        user_id: str,
        idempotency_key: str,
    ) -> GenerationRequestRecord | None:
        statement = select(GenerationRequestRecord).where(
            GenerationRequestRecord.user_id == user_id,
            GenerationRequestRecord.idempotency_key == idempotency_key,
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def save_generation_request(
        self,
        user_id: str,
        idempotency_key: str,
        request_hash: str,
        response: dict[str, Any],
    ) -> GenerationRequestRecord:
        record = GenerationRequestRecord(
            user_id=user_id,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_json=json.dumps(response),
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record
