from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.db import PantryItemRecord, PantryTransactionRecord


class PantryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_items(self, user_id: str) -> list[PantryItemRecord]:
        statement = (
            select(PantryItemRecord)
            .where(PantryItemRecord.user_id == user_id)
            .order_by(PantryItemRecord.display_name)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_item(self, user_id: str, item_id: int) -> PantryItemRecord | None:
        statement = select(PantryItemRecord).where(
            PantryItemRecord.user_id == user_id,
            PantryItemRecord.id == item_id,
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def upsert_items(self, user_id: str, values: list[dict[str, Any]]) -> list[PantryItemRecord]:
        saved: list[PantryItemRecord] = []
        for item_values in values:
            statement = select(PantryItemRecord).where(
                PantryItemRecord.user_id == user_id,
                PantryItemRecord.identity_key == item_values["identity_key"],
            )
            result = await self.session.execute(statement)
            record = result.scalars().first()
            if record is None:
                record = PantryItemRecord(user_id=user_id, **item_values)
                self.session.add(record)
            else:
                for key, value in item_values.items():
                    setattr(record, key, value)
                record.version += 1
                record.updated_at = datetime.now(UTC)
            saved.append(record)

        await self.session.commit()
        for record in saved:
            await self.session.refresh(record)
        return saved

    async def apply_transaction(
        self,
        item: PantryItemRecord,
        expected_version: int,
        quantity_value: Decimal,
        unit: str,
        transaction_type: str,
        transaction_quantity: Decimal,
        transaction_unit: str,
        source: str,
    ) -> tuple[PantryItemRecord, PantryTransactionRecord] | None:
        statement = (
            update(PantryItemRecord)
            .where(
                PantryItemRecord.id == item.id,
                PantryItemRecord.user_id == item.user_id,
                PantryItemRecord.version == expected_version,
            )
            .values(
                quantity_value=quantity_value,
                unit=unit,
                quantity_text=f"{quantity_value} {unit}",
                version=expected_version + 1,
                updated_at=datetime.now(UTC),
            )
        )
        result = await self.session.execute(statement)
        if result.rowcount != 1:
            await self.session.rollback()
            return None

        transaction = PantryTransactionRecord(
            pantry_item_id=item.id,
            transaction_type=transaction_type,
            quantity=transaction_quantity,
            unit=transaction_unit,
            resulting_quantity=quantity_value,
            source=source,
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        updated_item = await self.get_item(item.user_id, item.id)
        if updated_item is None:
            return None
        return updated_item, transaction

    async def list_transactions(self, user_id: str, item_id: int) -> list[PantryTransactionRecord] | None:
        if await self.get_item(user_id, item_id) is None:
            return None
        statement = (
            select(PantryTransactionRecord)
            .where(PantryTransactionRecord.pantry_item_id == item_id)
            .order_by(PantryTransactionRecord.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
