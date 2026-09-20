import json
import re
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

from app.domain.ingredients.models import Ingredient, IngredientMatch, IngredientOntology, MatchType

DEFAULT_ONTOLOGY_PATH = Path(__file__).parents[2] / "data" / "ingredients" / "ingredients_v1.json"
_DESCRIPTORS = {
    "approx",
    "approximately",
    "canned",
    "chopped",
    "crushed",
    "diced",
    "fresh",
    "frozen",
    "grated",
    "ground",
    "large",
    "medium",
    "optional",
    "organic",
    "raw",
    "ripe",
    "sliced",
    "small",
    "whole",
}
_QUANTITY_TOKEN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:kg|g|oz|lb|ml|l|tsp|tbsp|cups?|pieces?|pcs?|bunch(?:es)?|packets?|cans?|bottles?)?\b",
    re.IGNORECASE,
)


def _basic_normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("_", " ")
    return " ".join(re.sub(r"[^\w]+", " ", value, flags=re.UNICODE).split())


def _singularize(token: str) -> str:
    if len(token) <= 3:
        return token
    if token.endswith("ies"):
        return f"{token[:-3]}y"
    if token.endswith("oes"):
        return token[:-2]
    if token.endswith(("ches", "shes", "xes", "zes", "ses")):
        return token[:-2]
    if token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def normalize_ingredient_text(value: str) -> str:
    without_quantity = _QUANTITY_TOKEN.sub(" ", value)
    tokens = _basic_normalize(without_quantity).split()
    return " ".join(_singularize(token) for token in tokens if token not in _DESCRIPTORS)


@lru_cache(maxsize=8)
def load_ingredient_ontology(path: Path = DEFAULT_ONTOLOGY_PATH) -> tuple[Ingredient, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ontology = IngredientOntology.model_validate(payload)
    ids = [ingredient.id for ingredient in ontology.ingredients]
    canonical_names = [ingredient.canonical_name for ingredient in ontology.ingredients]
    if len(ids) != len(set(ids)) or len(canonical_names) != len(set(canonical_names)):
        raise ValueError("Ingredient ontology IDs and canonical names must be unique")
    return tuple(ontology.ingredients)


class IngredientNormalizer:
    def __init__(self, ingredients: Iterable[Ingredient] | None = None):
        self.ingredients = tuple(ingredients or load_ingredient_ontology())
        self._by_id = {ingredient.id: ingredient for ingredient in self.ingredients}
        self._canonical = self._build_index(
            (name, ingredient.id)
            for ingredient in self.ingredients
            for name in (ingredient.id, ingredient.canonical_name)
        )
        self._aliases = self._build_index(
            (name, ingredient.id)
            for ingredient in self.ingredients
            for name in (ingredient.display_name, *ingredient.aliases, *ingredient.regional_names.values())
        )
        self._token_index = self._build_index(
            (normalize_ingredient_text(name), ingredient.id)
            for ingredient in self.ingredients
            for name in (
                ingredient.id,
                ingredient.canonical_name,
                ingredient.display_name,
                *ingredient.aliases,
                *ingredient.regional_names.values(),
            )
        )

    @staticmethod
    def _build_index(pairs: Iterable[tuple[str, str]]) -> dict[str, set[str]]:
        index: dict[str, set[str]] = defaultdict(set)
        for name, ingredient_id in pairs:
            normalized = _basic_normalize(name)
            if normalized:
                index[normalized].add(ingredient_id)
        return dict(index)

    def normalize(self, query: str) -> IngredientMatch:
        basic = _basic_normalize(query)
        if not basic:
            return IngredientMatch(query=query, normalized_query="", match_type=MatchType.UNRESOLVED)

        match = self._match_ids(query, basic, self._canonical.get(basic), MatchType.CANONICAL)
        if match:
            return match
        match = self._match_ids(query, basic, self._aliases.get(basic), MatchType.ALIAS)
        if match:
            return match

        token_query = normalize_ingredient_text(query)
        match = self._match_ids(
            query,
            token_query,
            self._token_index.get(_basic_normalize(token_query)),
            MatchType.NORMALIZED_TOKEN,
        )
        if match:
            return match

        return self._fuzzy_match(query, token_query)

    def _match_ids(
        self,
        query: str,
        normalized_query: str,
        ingredient_ids: set[str] | None,
        match_type: MatchType,
    ) -> IngredientMatch | None:
        if not ingredient_ids:
            return None
        if len(ingredient_ids) > 1:
            return IngredientMatch(
                query=query,
                normalized_query=normalized_query,
                match_type=MatchType.AMBIGUOUS,
            )
        ingredient_id = next(iter(ingredient_ids))
        return IngredientMatch(
            query=query,
            normalized_query=normalized_query,
            match_type=match_type,
            ingredient=self._by_id[ingredient_id],
        )

    def _fuzzy_match(self, query: str, normalized_query: str) -> IngredientMatch:
        if len(normalized_query) < 5:
            return IngredientMatch(
                query=query,
                normalized_query=normalized_query,
                match_type=MatchType.UNRESOLVED,
            )

        scores: dict[str, float] = defaultdict(float)
        for known_name, ingredient_ids in self._token_index.items():
            score = SequenceMatcher(None, normalized_query, known_name).ratio()
            for ingredient_id in ingredient_ids:
                scores[ingredient_id] = max(scores[ingredient_id], score)

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        if not ranked or ranked[0][1] < 0.9:
            return IngredientMatch(
                query=query,
                normalized_query=normalized_query,
                match_type=MatchType.UNRESOLVED,
            )
        if len(ranked) > 1 and ranked[1][1] >= ranked[0][1] - 0.05:
            return IngredientMatch(
                query=query,
                normalized_query=normalized_query,
                match_type=MatchType.AMBIGUOUS,
            )
        return IngredientMatch(
            query=query,
            normalized_query=normalized_query,
            match_type=MatchType.FUZZY,
            ingredient=self._by_id[ranked[0][0]],
        )


ingredient_normalizer = IngredientNormalizer()
