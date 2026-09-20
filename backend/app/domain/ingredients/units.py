import re
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Unit(StrEnum):
    GRAM = "g"
    KILOGRAM = "kg"
    OUNCE = "oz"
    POUND = "lb"
    MILLILITER = "ml"
    LITER = "l"
    TEASPOON = "tsp"
    TABLESPOON = "tbsp"
    CUP = "cup"
    PIECE = "piece"
    BUNCH = "bunch"
    PACKET = "packet"
    CAN = "can"
    BOTTLE = "bottle"


class Quantity(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: Decimal = Field(ge=0)
    unit: Unit

    @field_validator("value", mode="before")
    @classmethod
    def decimal_from_input(cls, value: object) -> Decimal:
        return Decimal(str(value))


_UNIT_ALIASES = {
    "g": Unit.GRAM,
    "gram": Unit.GRAM,
    "grams": Unit.GRAM,
    "kg": Unit.KILOGRAM,
    "kilogram": Unit.KILOGRAM,
    "kilograms": Unit.KILOGRAM,
    "oz": Unit.OUNCE,
    "ounce": Unit.OUNCE,
    "ounces": Unit.OUNCE,
    "lb": Unit.POUND,
    "lbs": Unit.POUND,
    "pound": Unit.POUND,
    "pounds": Unit.POUND,
    "ml": Unit.MILLILITER,
    "milliliter": Unit.MILLILITER,
    "milliliters": Unit.MILLILITER,
    "millilitre": Unit.MILLILITER,
    "millilitres": Unit.MILLILITER,
    "l": Unit.LITER,
    "liter": Unit.LITER,
    "liters": Unit.LITER,
    "litre": Unit.LITER,
    "litres": Unit.LITER,
    "tsp": Unit.TEASPOON,
    "teaspoon": Unit.TEASPOON,
    "teaspoons": Unit.TEASPOON,
    "tbsp": Unit.TABLESPOON,
    "tablespoon": Unit.TABLESPOON,
    "tablespoons": Unit.TABLESPOON,
    "cup": Unit.CUP,
    "cups": Unit.CUP,
    "piece": Unit.PIECE,
    "pieces": Unit.PIECE,
    "pc": Unit.PIECE,
    "pcs": Unit.PIECE,
    "bunch": Unit.BUNCH,
    "bunches": Unit.BUNCH,
    "packet": Unit.PACKET,
    "packets": Unit.PACKET,
    "pack": Unit.PACKET,
    "packs": Unit.PACKET,
    "can": Unit.CAN,
    "cans": Unit.CAN,
    "bottle": Unit.BOTTLE,
    "bottles": Unit.BOTTLE,
}

_WEIGHT_FACTORS = {
    Unit.GRAM: Decimal("1"),
    Unit.KILOGRAM: Decimal("1000"),
    Unit.OUNCE: Decimal("28.349523125"),
    Unit.POUND: Decimal("453.59237"),
}

_VOLUME_FACTORS = {
    Unit.MILLILITER: Decimal("1"),
    Unit.LITER: Decimal("1000"),
    Unit.TEASPOON: Decimal("4.92892159375"),
    Unit.TABLESPOON: Decimal("14.78676478125"),
    Unit.CUP: Decimal("236.5882365"),
}

_QUANTITY_PATTERN = re.compile(r"^\s*(\d+(?:\.\d+)?|\.\d+)\s*([A-Za-z]+)\.?\s*$")


def normalize_unit(value: str) -> Unit | None:
    return _UNIT_ALIASES.get(value.strip().casefold().rstrip("."))


def parse_quantity(value: str) -> Quantity:
    match = _QUANTITY_PATTERN.fullmatch(value.replace(",", ""))
    if not match:
        raise ValueError(f"Unsupported quantity format: {value!r}")
    unit = normalize_unit(match.group(2))
    if unit is None:
        raise ValueError(f"Unsupported unit: {match.group(2)!r}")
    return Quantity(value=match.group(1), unit=unit)


def convert_quantity(quantity: Quantity, target_unit: Unit) -> Quantity:
    if quantity.unit == target_unit:
        return quantity

    for factors in (_WEIGHT_FACTORS, _VOLUME_FACTORS):
        if quantity.unit in factors and target_unit in factors:
            base_value = quantity.value * factors[quantity.unit]
            return Quantity(value=base_value / factors[target_unit], unit=target_unit)

    raise ValueError(f"Cannot convert {quantity.unit.value} to {target_unit.value} without ingredient-specific data")
