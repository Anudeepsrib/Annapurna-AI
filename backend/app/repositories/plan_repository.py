import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.db import MealPlan
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
