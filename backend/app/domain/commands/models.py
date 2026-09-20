from enum import StrEnum

from pydantic import BaseModel, Field


class HouseholdCommandType(StrEnum):
    REPLACE_MEAL = "REPLACE_MEAL"
    EXCLUDE_SHOPPING_ITEM = "EXCLUDE_SHOPPING_ITEM"
    USE_PANTRY_SOON = "USE_PANTRY_SOON"
    ADD_GUESTS = "ADD_GUESTS"
    ADD_SHOPPING_ITEM = "ADD_SHOPPING_ITEM"


class HouseholdCommandRequest(BaseModel):
    text: str = Field(min_length=1, max_length=300)
