from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from app.domain.ingredients import IngredientCategory, StorageLocation, Unit


class PantryTransactionType(StrEnum):
    PURCHASE = "PURCHASE"
    CONSUME = "CONSUME"
    ADJUST = "ADJUST"
    EXPIRE = "EXPIRE"
    DISCARD = "DISCARD"
    RESTOCK = "RESTOCK"


class PantryImportRequest(BaseModel):
    pantryText: str = Field(max_length=5000)


class PantryItemView(BaseModel):
    id: int
    ingredientId: str | None
    displayName: str
    quantity: str | None
    unit: Unit | None
    quantityText: str
    category: IngredientCategory
    storageLocation: StorageLocation
    opened: bool
    expiresAt: datetime | None
    expired: bool
    minimumStockQuantity: str | None
    minimumStockUnit: Unit | None
    preferredBrand: str
    notes: str
    version: int


class PantryTransactionRequest(BaseModel):
    transactionType: PantryTransactionType
    quantity: Decimal = Field(ge=0)
    unit: Unit
    expectedVersion: int = Field(ge=1)
    source: str = Field(default="manual", min_length=1, max_length=80)

    @model_validator(mode="after")
    def require_positive_delta(self) -> "PantryTransactionRequest":
        if self.transactionType != PantryTransactionType.ADJUST and self.quantity == 0:
            raise ValueError("quantity must be greater than zero for this transaction type")
        return self


class PantryTransactionView(BaseModel):
    id: int
    pantryItemId: int
    transactionType: PantryTransactionType
    quantity: str
    unit: Unit
    resultingQuantity: str | None
    createdAt: datetime
    source: str
