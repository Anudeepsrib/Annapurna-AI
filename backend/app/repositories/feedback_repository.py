from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.db import LeftoverRecord, MealExecutionRecord, MealFeedbackRecord


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_executions(self, user_id: str, plan_id: int, day: str) -> list[MealExecutionRecord]:
        result = await self.session.execute(
            select(MealExecutionRecord).where(
                MealExecutionRecord.user_id == user_id,
                MealExecutionRecord.plan_id == plan_id,
                MealExecutionRecord.day == day,
            )
        )
        return list(result.scalars().all())

    async def set_execution(
        self,
        user_id: str,
        plan_id: int,
        day: str,
        meal_type: str,
        status: str,
    ) -> MealExecutionRecord:
        result = await self.session.execute(
            select(MealExecutionRecord).where(
                MealExecutionRecord.user_id == user_id,
                MealExecutionRecord.plan_id == plan_id,
                MealExecutionRecord.day == day,
                MealExecutionRecord.meal_type == meal_type,
            )
        )
        record = result.scalars().first()
        if record is None:
            record = MealExecutionRecord(
                user_id=user_id,
                plan_id=plan_id,
                day=day,
                meal_type=meal_type,
                status=status,
            )
            self.session.add(record)
        else:
            record.status = status
            record.updated_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def list_feedback(self, user_id: str, plan_id: int, day: str) -> list[MealFeedbackRecord]:
        result = await self.session.execute(
            select(MealFeedbackRecord).where(
                MealFeedbackRecord.user_id == user_id,
                MealFeedbackRecord.plan_id == plan_id,
                MealFeedbackRecord.day == day,
            )
        )
        return list(result.scalars().all())

    async def add_feedback(
        self,
        user_id: str,
        plan_id: int,
        day: str,
        meal_type: str,
        signal: str,
    ) -> MealFeedbackRecord:
        result = await self.session.execute(
            select(MealFeedbackRecord).where(
                MealFeedbackRecord.user_id == user_id,
                MealFeedbackRecord.plan_id == plan_id,
                MealFeedbackRecord.day == day,
                MealFeedbackRecord.meal_type == meal_type,
                MealFeedbackRecord.signal == signal,
            )
        )
        record = result.scalars().first()
        if record is None:
            record = MealFeedbackRecord(
                user_id=user_id,
                plan_id=plan_id,
                day=day,
                meal_type=meal_type,
                signal=signal,
            )
            self.session.add(record)
            await self.session.commit()
            await self.session.refresh(record)
        return record

    async def upsert_leftover(
        self,
        user_id: str,
        plan_id: int,
        day: str,
        meal_type: str,
        title: str,
        servings_remaining: int,
        usable_until: datetime,
    ) -> LeftoverRecord:
        result = await self.session.execute(
            select(LeftoverRecord).where(
                LeftoverRecord.user_id == user_id,
                LeftoverRecord.source_plan_id == plan_id,
                LeftoverRecord.source_day == day,
                LeftoverRecord.source_meal_type == meal_type,
            )
        )
        record = result.scalars().first()
        if record is None:
            record = LeftoverRecord(
                user_id=user_id,
                source_plan_id=plan_id,
                source_day=day,
                source_meal_type=meal_type,
                title=title,
                servings_remaining=servings_remaining,
                usable_until=usable_until,
            )
            self.session.add(record)
        else:
            record.title = title
            record.servings_remaining = servings_remaining
            record.usable_until = usable_until
            record.consumed = False
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def list_active_leftovers(self, user_id: str) -> list[LeftoverRecord]:
        result = await self.session.execute(
            select(LeftoverRecord)
            .where(
                LeftoverRecord.user_id == user_id,
                LeftoverRecord.consumed.is_(False),
                LeftoverRecord.usable_until >= datetime.now(UTC),
            )
            .order_by(LeftoverRecord.usable_until)
        )
        return list(result.scalars().all())
