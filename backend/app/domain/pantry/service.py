import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PantryConflictError
from app.domain.ingredients import (
    IngredientCategory,
    Quantity,
    StorageLocation,
    Unit,
    convert_quantity,
    ingredient_normalizer,
    parse_quantity,
)
from app.domain.pantry.models import (
    PantryItemView,
    PantryTransactionRequest,
    PantryTransactionType,
    PantryTransactionView,
)
from app.models.db import PantryItemRecord, PantryTransactionRecord
from app.models.schemas import PantryItem, PlanRequest
from app.repositories.pantry_repository import PantryRepository

_EXPIRY_PATTERN = re.compile(
    r"(?:use within|expires within|expires in|expires)\s+(\d+)\s*days?",
    re.IGNORECASE,
)
_TRAILING_QUANTITY_PATTERN = re.compile(r"^(.*?)\s+(\d+(?:\.\d+)?\s*[A-Za-z]+)$")
_LEGACY_TO_CATEGORY = {
    "grains": IngredientCategory.GRAINS,
    "dals": IngredientCategory.DALS_LEGUMES,
    "vegetables": IngredientCategory.PRODUCE,
    "spices": IngredientCategory.SPICES,
    "dairy": IngredientCategory.DAIRY,
    "other": IngredientCategory.OTHER,
}
_CATEGORY_TO_LEGACY = {
    IngredientCategory.GRAINS: "grains",
    IngredientCategory.DALS_LEGUMES: "dals",
    IngredientCategory.PRODUCE: "vegetables",
    IngredientCategory.SPICES: "spices",
    IngredientCategory.DAIRY: "dairy",
}


def _format_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class PantryService:
    def __init__(self, session: AsyncSession):
        self.repository = PantryRepository(session)

    async def prepare_plan_request(self, user_id: str, request: PlanRequest) -> PlanRequest:
        if request.pantryText is not None:
            pantry_items = self.parse_text(request.pantryText)
        elif "pantryInventory" in request.model_fields_set:
            pantry_items = request.pantryInventory
        else:
            pantry_items = [self.to_legacy(record) for record in await self.repository.list_items(user_id)]

        if pantry_items:
            records = await self.upsert_items(user_id, pantry_items)
            pantry_items = [self.to_legacy(record) for record in records]

        return request.model_copy(update={"pantryInventory": pantry_items})

    def parse_text(self, text: str) -> list[PantryItem]:
        items: list[PantryItem] = []
        for raw_line in text.splitlines()[:80]:
            line = raw_line.strip().lstrip("•* ")
            if not line:
                continue
            expiry_match = _EXPIRY_PATTERN.search(line)
            expires_within_days = int(expiry_match.group(1)) if expiry_match else None
            if expiry_match:
                line = _EXPIRY_PATTERN.sub("", line).strip(" ,-;")

            parts = re.split(r"\s+-\s+", line, maxsplit=1)
            if len(parts) == 2:
                name, quantity = parts
            else:
                trailing = _TRAILING_QUANTITY_PATTERN.fullmatch(line)
                name, quantity = trailing.groups() if trailing else (line, "")

            items.append(
                PantryItem(
                    name=name.strip(),
                    quantity=quantity.strip(),
                    expiresWithinDays=expires_within_days,
                )
            )
        return items

    async def import_text(self, user_id: str, text: str) -> list[PantryItemView]:
        return [self.to_view(record) for record in await self.upsert_items(user_id, self.parse_text(text))]

    async def upsert_items(self, user_id: str, items: list[PantryItem]) -> list[PantryItemRecord]:
        deduplicated: dict[str, dict] = {}
        for item in items:
            values = self._record_values(item)
            deduplicated[values["identity_key"]] = values
        if not deduplicated:
            return []
        return await self.repository.upsert_items(user_id, list(deduplicated.values()))

    async def list_items(self, user_id: str) -> list[PantryItemView]:
        return [self.to_view(record) for record in await self.repository.list_items(user_id)]

    async def current_legacy_items(self, user_id: str) -> list[PantryItem]:
        return [self.to_legacy(record) for record in await self.repository.list_items(user_id)]

    async def record_transaction(
        self,
        user_id: str,
        item_id: int,
        request: PantryTransactionRequest,
    ) -> tuple[PantryItemView, PantryTransactionView]:
        item = await self.repository.get_item(user_id, item_id)
        if item is None:
            raise NotFoundError("Pantry item")

        incoming = Quantity(value=request.quantity, unit=request.unit)
        if item.quantity_value is None or item.unit is None:
            if request.transactionType in {
                PantryTransactionType.CONSUME,
                PantryTransactionType.EXPIRE,
                PantryTransactionType.DISCARD,
            }:
                raise PantryConflictError("Pantry quantity is unresolved; adjust it before subtracting stock")
            current = Quantity(value=0, unit=incoming.unit)
        else:
            current = Quantity(value=item.quantity_value, unit=Unit(item.unit))
            try:
                incoming = convert_quantity(incoming, current.unit)
            except ValueError as exc:
                raise PantryConflictError(str(exc)) from exc

        if request.transactionType in {PantryTransactionType.PURCHASE, PantryTransactionType.RESTOCK}:
            resulting_value = current.value + incoming.value
        elif request.transactionType == PantryTransactionType.ADJUST:
            resulting_value = incoming.value
        else:
            if incoming.value > current.value:
                raise PantryConflictError("Transaction quantity exceeds available pantry stock")
            resulting_value = current.value - incoming.value

        saved = await self.repository.apply_transaction(
            item=item,
            expected_version=request.expectedVersion,
            quantity_value=resulting_value,
            unit=current.unit.value,
            transaction_type=request.transactionType.value,
            transaction_quantity=request.quantity,
            transaction_unit=request.unit.value,
            source=request.source,
        )
        if saved is None:
            raise PantryConflictError("Pantry item changed; refresh it and retry with the latest version")
        updated_item, transaction = saved
        return self.to_view(updated_item), self.to_transaction_view(transaction)

    async def list_transactions(self, user_id: str, item_id: int) -> list[PantryTransactionView]:
        transactions = await self.repository.list_transactions(user_id, item_id)
        if transactions is None:
            raise NotFoundError("Pantry item")
        return [self.to_transaction_view(transaction) for transaction in transactions]

    def _record_values(self, item: PantryItem) -> dict:
        match = ingredient_normalizer.normalize(item.name)
        ingredient = match.ingredient
        identity_key = (
            f"ingredient:{ingredient.id}" if ingredient is not None else f"unresolved:{match.normalized_query}"
        )
        default_unit = ingredient.default_unit if ingredient is not None else None
        quantity = self._parse_quantity(item.quantity, default_unit)
        minimum_stock = self._parse_quantity(item.minimumStockQuantity, quantity.unit if quantity else default_unit)

        expires_at = item.expiresAt
        if expires_at is None and item.expiresWithinDays is not None:
            expires_at = datetime.now(UTC) + timedelta(days=item.expiresWithinDays)
        if expires_at is None and item.expired:
            expires_at = datetime.now(UTC) - timedelta(days=1)

        return {
            "identity_key": identity_key,
            "ingredient_id": ingredient.id if ingredient is not None else None,
            "display_name": ingredient.display_name if ingredient is not None else item.name,
            "quantity_value": quantity.value if quantity else None,
            "unit": quantity.unit.value if quantity else None,
            "quantity_text": item.quantity,
            "category": (
                ingredient.category.value if ingredient is not None else _LEGACY_TO_CATEGORY[item.category].value
            ),
            "storage_location": (
                item.storageLocation
                or (ingredient.storage_location.value if ingredient is not None else StorageLocation.PANTRY.value)
            ),
            "opened": item.opened,
            "expires_at": expires_at,
            "minimum_stock_quantity": minimum_stock.value if minimum_stock else None,
            "minimum_stock_unit": minimum_stock.unit.value if minimum_stock else None,
            "preferred_brand": item.preferredBrand,
            "notes": item.notes,
        }

    def _parse_quantity(self, raw_value: str, default_unit: Unit | None) -> Quantity | None:
        value = raw_value.strip()
        if not value:
            return None
        try:
            return parse_quantity(value)
        except ValueError:
            if default_unit is None:
                return None
            try:
                return Quantity(value=Decimal(value), unit=default_unit)
            except (InvalidOperation, ValueError):
                return None

    def to_legacy(self, record: PantryItemRecord) -> PantryItem:
        now = datetime.now(UTC)
        expires_at = _as_utc(record.expires_at) if record.expires_at else None
        expired = expires_at is not None and expires_at < now
        expires_within_days = None
        if expires_at is not None and not expired:
            expires_within_days = max(0, ceil((expires_at - now).total_seconds() / 86400))

        quantity = record.quantity_text
        if record.quantity_value is not None and record.unit is not None:
            quantity = f"{_format_decimal(record.quantity_value)} {record.unit}"

        category = IngredientCategory(record.category)
        return PantryItem(
            name=record.display_name,
            quantity=quantity,
            category=_CATEGORY_TO_LEGACY.get(category, "other"),
            expiresWithinDays=expires_within_days,
            storageLocation=record.storage_location,
            opened=record.opened,
            expiresAt=record.expires_at,
            expired=expired,
            minimumStockQuantity=(
                f"{_format_decimal(record.minimum_stock_quantity)} {record.minimum_stock_unit}"
                if record.minimum_stock_quantity is not None and record.minimum_stock_unit
                else ""
            ),
            preferredBrand=record.preferred_brand,
            notes=record.notes,
        )

    def to_view(self, record: PantryItemRecord) -> PantryItemView:
        expires_at = _as_utc(record.expires_at) if record.expires_at else None
        return PantryItemView(
            id=record.id,
            ingredientId=record.ingredient_id,
            displayName=record.display_name,
            quantity=_format_decimal(record.quantity_value),
            unit=Unit(record.unit) if record.unit else None,
            quantityText=record.quantity_text,
            category=IngredientCategory(record.category),
            storageLocation=StorageLocation(record.storage_location),
            opened=record.opened,
            expiresAt=record.expires_at,
            expired=expires_at is not None and expires_at < datetime.now(UTC),
            minimumStockQuantity=_format_decimal(record.minimum_stock_quantity),
            minimumStockUnit=Unit(record.minimum_stock_unit) if record.minimum_stock_unit else None,
            preferredBrand=record.preferred_brand,
            notes=record.notes,
            version=record.version,
        )

    def to_transaction_view(self, transaction: PantryTransactionRecord) -> PantryTransactionView:
        return PantryTransactionView(
            id=transaction.id,
            pantryItemId=transaction.pantry_item_id,
            transactionType=PantryTransactionType(transaction.transaction_type),
            quantity=_format_decimal(transaction.quantity),
            unit=Unit(transaction.unit),
            resultingQuantity=_format_decimal(transaction.resulting_quantity),
            createdAt=transaction.created_at,
            source=transaction.source,
        )
