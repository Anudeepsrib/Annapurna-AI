import json
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domain.ingredients import (
    Ingredient,
    IngredientCategory,
    IngredientNormalizer,
    MatchType,
    Quantity,
    StorageLocation,
    Unit,
    convert_quantity,
    ingredient_normalizer,
    normalize_unit,
    parse_quantity,
)


def test_ontology_is_curated_unique_and_right_sized():
    ingredients = ingredient_normalizer.ingredients

    assert 100 <= len(ingredients) <= 200
    assert len({ingredient.id for ingredient in ingredients}) == len(ingredients)
    assert len({ingredient.canonical_name for ingredient in ingredients}) == len(ingredients)
    assert all(ingredient.display_name and ingredient.default_unit for ingredient in ingredients)


@pytest.mark.parametrize(
    ("query", "ingredient_id"),
    [
        ("pigeon_pea", "pigeon_pea"),
        ("toor dal", "pigeon_pea"),
        ("kandi pappu", "pigeon_pea"),
        ("కందిపప్పు", "pigeon_pea"),
        ("fresh tomatoes - 2", "tomato"),
        ("organic roma tomatoes", "tomato"),
        ("palakura", "spinach"),
    ],
)
def test_normalizer_resolves_canonical_alias_regional_and_token_forms(query: str, ingredient_id: str):
    match = ingredient_normalizer.normalize(query)

    assert match.ingredient is not None
    assert match.ingredient.id == ingredient_id


def test_normalizer_uses_conservative_fuzzy_matching_and_preserves_unknowns():
    fuzzy = ingredient_normalizer.normalize("tomatto")
    unknown = ingredient_normalizer.normalize("dragon fruit powder")

    assert fuzzy.match_type == MatchType.FUZZY
    assert fuzzy.ingredient is not None and fuzzy.ingredient.id == "tomato"
    assert unknown.match_type == MatchType.UNRESOLVED
    assert unknown.ingredient is None


def test_normalizer_never_silently_resolves_ambiguous_aliases():
    shared = {
        "aliases": ["greens"],
        "regional_names": {},
        "category": IngredientCategory.PRODUCE,
        "default_unit": Unit.BUNCH,
        "storage_location": StorageLocation.REFRIGERATOR,
        "vegetarian": True,
        "allergens": [],
        "approximate_shelf_life_days": 4,
    }
    normalizer = IngredientNormalizer(
        [
            Ingredient(id="leaf_one", canonical_name="leaf_one", display_name="Leaf One", **shared),
            Ingredient(id="leaf_two", canonical_name="leaf_two", display_name="Leaf Two", **shared),
        ]
    )

    match = normalizer.normalize("greens")

    assert match.match_type == MatchType.AMBIGUOUS
    assert match.ingredient is None


@pytest.mark.parametrize(
    ("raw_unit", "unit"),
    [
        ("grams", Unit.GRAM),
        ("KG", Unit.KILOGRAM),
        ("ounces", Unit.OUNCE),
        ("lbs", Unit.POUND),
        ("millilitres", Unit.MILLILITER),
        ("liters", Unit.LITER),
        ("teaspoons", Unit.TEASPOON),
        ("tablespoons", Unit.TABLESPOON),
        ("cups", Unit.CUP),
        ("pieces", Unit.PIECE),
        ("bunches", Unit.BUNCH),
        ("packets", Unit.PACKET),
        ("cans", Unit.CAN),
        ("bottles", Unit.BOTTLE),
    ],
)
def test_required_unit_aliases_are_supported(raw_unit: str, unit: Unit):
    assert normalize_unit(raw_unit) == unit


def test_quantity_parsing_and_same_dimension_conversion_are_decimal_based():
    kilograms = parse_quantity("2 kg")
    grams = convert_quantity(kilograms, Unit.GRAM)

    assert kilograms == Quantity(value=Decimal("2"), unit=Unit.KILOGRAM)
    assert grams == Quantity(value=Decimal("2000"), unit=Unit.GRAM)
    assert convert_quantity(parse_quantity("2000 g"), Unit.KILOGRAM).value == Decimal("2")


def test_unit_conversion_refuses_cross_dimension_and_package_guesses():
    with pytest.raises(ValueError, match="without ingredient-specific data"):
        convert_quantity(parse_quantity("1 kg"), Unit.CUP)
    with pytest.raises(ValueError, match="without ingredient-specific data"):
        convert_quantity(parse_quantity("1 bottle"), Unit.MILLILITER)


def test_grocery_matching_uses_canonical_alias_identity(client: TestClient):
    payload = {
        "householdSize": "2",
        "spiceLevel": "medium",
        "dietary": "vegetarian",
        "pantryInventory": [{"name": "kandi pappu", "quantity": "1 kg", "category": "dals"}],
    }

    with patch("app.services.plan_service.llm_service.generate_response", return_value="not json"):
        response = client.post("/api/v1/generate-plan", json=payload)

    assert response.status_code == 200
    pantry = next(
        category for category in response.json()["grocery_optimization"] if category["name"] == "Use From Pantry First"
    )
    toor_dal = next(item for item in pantry["items"] if item["id"] == "pigeon_pea")
    assert toor_dal["status"] == "pantry"
    assert toor_dal["quantity"] == "1 kg"
    assert "pigeon_pea" not in json.dumps(response.json()["plan"])
