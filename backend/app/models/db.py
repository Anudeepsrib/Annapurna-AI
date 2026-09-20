import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel


class MealPlan(SQLModel, table=True):
    """
    Database model for storing generated meal plans.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Store the JSON blob of the plan directly
    # In a larger app, we might normalize meals into separate tables,
    # but for this MVP, storing the complex JSON structure is efficient.
    plan_json: str  # JSON stringified content
    generation_metadata_json: Optional[str] = None

    @property
    def plan_data(self):
        return json.loads(self.plan_json)

    @plan_data.setter
    def plan_data(self, value):
        self.plan_json = json.dumps(value)

    @property
    def generation_metadata(self) -> dict:
        if not self.generation_metadata_json:
            return {}
        return json.loads(self.generation_metadata_json)


class PantryItemRecord(SQLModel, table=True):
    __tablename__ = "pantry_item"
    __table_args__ = (UniqueConstraint("user_id", "identity_key", name="uq_pantry_item_user_identity"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    identity_key: str
    ingredient_id: str | None = Field(default=None, index=True)
    display_name: str
    quantity_value: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(14, 3), nullable=True),
    )
    unit: str | None = None
    quantity_text: str = ""
    category: str
    storage_location: str
    opened: bool = False
    expires_at: datetime | None = None
    minimum_stock_quantity: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(14, 3), nullable=True),
    )
    minimum_stock_unit: str | None = None
    preferred_brand: str = ""
    notes: str = ""
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PantryTransactionRecord(SQLModel, table=True):
    __tablename__ = "pantry_transaction"

    id: Optional[int] = Field(default=None, primary_key=True)
    pantry_item_id: int = Field(foreign_key="pantry_item.id", index=True)
    transaction_type: str
    quantity: Decimal = Field(sa_column=Column(Numeric(14, 3), nullable=False))
    unit: str
    resulting_quantity: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(14, 3), nullable=True),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: str = "manual"


class MealExecutionRecord(SQLModel, table=True):
    __tablename__ = "meal_execution"
    __table_args__ = (
        UniqueConstraint("user_id", "plan_id", "day", "meal_type", name="uq_meal_execution_slot"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    plan_id: int = Field(foreign_key="mealplan.id", index=True)
    day: str
    meal_type: str
    status: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MealFeedbackRecord(SQLModel, table=True):
    __tablename__ = "meal_feedback"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "plan_id",
            "day",
            "meal_type",
            "signal",
            name="uq_meal_feedback_signal",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    plan_id: int = Field(foreign_key="mealplan.id", index=True)
    day: str
    meal_type: str
    signal: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LeftoverRecord(SQLModel, table=True):
    __tablename__ = "leftover"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "source_plan_id",
            "source_day",
            "source_meal_type",
            name="uq_leftover_source_meal",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    source_plan_id: int = Field(foreign_key="mealplan.id", index=True)
    source_day: str
    source_meal_type: str
    title: str
    servings_remaining: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    usable_until: datetime
    consumed: bool = False
