from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.pantry.models import PantryItemView
from app.models.schemas import PlanMeal


class MealType(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"


class MealStatus(StrEnum):
    COOKED = "COOKED"
    SKIPPED = "SKIPPED"
    LEFTOVER = "LEFTOVER"
    ATE_OUT = "ATE_OUT"
    REPLACED = "REPLACED"


class FeedbackSignal(StrEnum):
    LIKED = "LIKED"
    DISLIKED = "DISLIKED"
    TOO_SPICY = "TOO_SPICY"
    TOO_MUCH_WORK = "TOO_MUCH_WORK"
    WOULD_REPEAT = "WOULD_REPEAT"
    WOULD_NOT_REPEAT = "WOULD_NOT_REPEAT"


class MealStatusRequest(BaseModel):
    status: MealStatus
    servingsRemaining: int | None = Field(default=None, ge=1, le=24)
    usableUntil: datetime | None = None


class FeedbackRequest(BaseModel):
    signal: FeedbackSignal


class LeftoverUpdateRequest(BaseModel):
    servingsRemaining: int | None = Field(default=None, ge=0, le=24)
    usableUntil: datetime | None = None
    consumed: bool | None = None


class MealActivityView(BaseModel):
    mealType: MealType
    meal: PlanMeal
    status: MealStatus | None = None
    feedback: list[FeedbackSignal] = Field(default_factory=list)
    missingIngredients: list[str] = Field(default_factory=list)


class LeftoverView(BaseModel):
    id: int
    title: str
    sourceDay: str
    sourceMealType: MealType
    servingsRemaining: int
    createdAt: datetime
    usableUntil: datetime


class TodayView(BaseModel):
    day: str
    date: str
    meals: list[MealActivityView]
    expiringPantry: list[PantryItemView]
    leftovers: list[LeftoverView]
    planAvailable: Literal[True] = True


class EmptyTodayView(BaseModel):
    planAvailable: Literal[False] = False
    day: str
    date: str
    meals: list = Field(default_factory=list)
    expiringPantry: list[PantryItemView] = Field(default_factory=list)
    leftovers: list[LeftoverView] = Field(default_factory=list)
