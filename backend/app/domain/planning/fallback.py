import re
from typing import Any

from app.core.safety import NUTRITION_ESTIMATE_DISCLAIMER, WELLNESS_DISCLAIMER
from app.domain.planning.models import CompiledConstraints
from app.domain.planning.validator import restricted_terms

FALLBACK_PLANNER_VERSION = "deterministic_fallback_v1"


class FallbackPlanner:
    def build(
        self,
        source_status: str,
        safety_notes: list[str],
        constraints: CompiledConstraints,
    ) -> list[dict[str, Any]]:
        avoided_terms = restricted_terms(constraints)
        days = [
            ("Monday", "Day 1", "Pesarattu", "Andhra Pappu & Rice", "Phulka & Bendakaya Fry"),
            ("Tuesday", "Day 2", "Idli Sambar", "Gutti Vankaya", "Vegetable Pulao"),
            ("Wednesday", "Day 3", "Upma", "Dosakaya Pappu", "Tomato Rice"),
            ("Thursday", "Day 4", "Dosa", "Sambar Rice", "Cabbage Poriyal with Rotis"),
            ("Friday", "Day 5", "Pongal", "Palakura Pappu", "Lemon Rice with Sundal"),
            ("Saturday", "Day 6", "Uttapam", "Vegetable Kurma with Rice", "Millet Khichdi"),
            ("Sunday", "Day 7", "Ragi Dosa", "Mamidikaya Pappu", "Curd Rice with Tempered Vegetables"),
        ]

        plan: list[dict[str, Any]] = []
        for day, date, breakfast, lunch, dinner in days:
            breakfast = _safe_meal_name(breakfast, avoided_terms)
            lunch = _safe_meal_name(lunch, avoided_terms)
            dinner = _safe_meal_name(dinner, avoided_terms)
            plan.append(
                {
                    "day": day,
                    "date": date,
                    "confidence": "low",
                    "source_status": source_status,
                    "disclaimer": WELLNESS_DISCLAIMER,
                    "safety_notes": safety_notes,
                    "meals": {
                        "breakfast": _meal(
                            breakfast,
                            "A familiar vegetarian breakfast adjusted for the requested spice level.",
                            _ingredients_for(breakfast, avoided_terms),
                            "8:00 AM",
                            source_status,
                        ),
                        "lunch": _meal(
                            lunch,
                            "A rice-and-dal centered meal pattern for everyday home cooking.",
                            _ingredients_for(lunch, avoided_terms),
                            "1:00 PM",
                            source_status,
                        ),
                        "dinner": _meal(
                            dinner,
                            "A lighter dinner idea using common pantry ingredients.",
                            _ingredients_for(dinner, avoided_terms),
                            "7:30 PM",
                            source_status,
                        ),
                    },
                }
            )
        return plan


def _meal(
    title: str,
    description: str,
    ingredients: list[str],
    time: str,
    source_status: str,
) -> dict[str, Any]:
    return {
        "title": title,
        "description": description,
        "ingredients": ingredients,
        "time": time,
        "nutrition": {
            "calories_kcal": None,
            "protein_g": None,
            "carbs_g": None,
            "fat_g": None,
            "fiber_g": None,
        },
        "confidence": "low",
        "source_status": source_status,
        "disclaimer": NUTRITION_ESTIMATE_DISCLAIMER,
    }


def _safe_meal_name(meal_name: str, avoided_terms: tuple[str, ...]) -> str:
    return "Vegetable Rice" if _contains_any(meal_name, avoided_terms) else meal_name


def _ingredients_for(meal_name: str, avoided_terms: tuple[str, ...]) -> list[str]:
    base: dict[str, list[str]] = {
        "Pesarattu": ["green gram", "ginger", "green chili", "rice"],
        "Andhra Pappu & Rice": ["toor dal", "tomato", "rice", "tempering spices"],
        "Phulka & Bendakaya Fry": ["okra", "whole wheat flour", "onion", "spices"],
        "Idli Sambar": ["rice", "urad dal", "toor dal", "mixed vegetables"],
        "Gutti Vankaya": ["brinjal", "sesame", "coconut", "tamarind", "rice"],
        "Vegetable Pulao": ["rice", "carrot", "beans", "spices"],
        "Upma": ["rava", "mustard seeds", "curry leaves", "vegetables"],
        "Dosakaya Pappu": ["yellow cucumber", "toor dal", "tomato", "rice"],
        "Tomato Rice": ["rice", "tomato", "curry leaves", "tempering spices"],
        "Dosa": ["rice", "urad dal", "fenugreek", "coconut chutney"],
        "Sambar Rice": ["rice", "toor dal", "sambar powder", "vegetables"],
        "Cabbage Poriyal with Rotis": ["cabbage", "whole wheat flour", "coconut", "mustard seeds"],
        "Pongal": ["rice", "moong dal", "black pepper", "cumin"],
        "Palakura Pappu": ["spinach", "toor dal", "tamarind", "rice"],
        "Lemon Rice with Sundal": ["rice", "lemon", "chana", "curry leaves"],
        "Uttapam": ["rice batter", "onion", "tomato", "coriander"],
        "Vegetable Kurma with Rice": ["rice", "mixed vegetables", "coconut", "spices"],
        "Millet Khichdi": ["millet", "moong dal", "vegetables", "cumin"],
        "Ragi Dosa": ["ragi flour", "rice flour", "cumin", "coriander"],
        "Mamidikaya Pappu": ["raw mango", "toor dal", "rice", "tempering spices"],
        "Curd Rice with Tempered Vegetables": ["rice", "dairy", "carrot", "mustard seeds"],
    }
    ingredients = base.get(meal_name, ["rice", "dal", "vegetables", "spices"])
    filtered = [item for item in ingredients if not _contains_any(item, avoided_terms)]
    return filtered or ["rice", "vegetables", "tempering spices"]


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    value = text.casefold()
    return any(re.search(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", value) for term in terms)
