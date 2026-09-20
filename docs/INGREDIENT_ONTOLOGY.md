# Ingredient Ontology V1

Annapurna's first ingredient ontology is a curated local JSON file containing
138 ingredients used commonly in Telugu, Andhra, and broader South Indian home
cooking. It is intentionally small enough to review by hand.

Each record contains a stable ID, canonical and display names, aliases, selected
Telugu names, category, default unit, storage location, vegetarian status,
allergens, and an approximate shelf-life hint. Shelf-life values are planning
hints, not food-safety guarantees.

## Resolution order

`IngredientNormalizer` resolves input in this order:

1. Exact canonical ID or canonical name.
2. Exact display name, alias, or regional name.
3. Normalized tokens after removing quantities and preparation descriptors and
   applying conservative singularization.
4. Conservative standard-library fuzzy matching with a high threshold and a
   uniqueness margin.
5. Explicit `ambiguous` or `unresolved` result.

The normalizer never silently chooses between multiple candidates. The grocery
optimizer now uses canonical identity, so `toor dal`, `kandi pappu`, and
`కందిపప్పు` reconcile to the same pantry item while retaining existing display
text in API responses.

## Quantities and units

Quantities use `Decimal` plus a typed unit. Supported units are:

- Weight: `g`, `kg`, `oz`, `lb`
- Volume: `ml`, `l`, `tsp`, `tbsp`, `cup`
- Count/package: `piece`, `bunch`, `packet`, `can`, `bottle`

Weight converts only to weight, and volume only to volume. Count and package
units have no implicit conversion. Weight-to-volume conversion is rejected
until an ingredient-specific density is available.

## Updating the seed

Edit `backend/app/data/ingredients/ingredients_v1.json`, retain stable IDs, and
run `pytest tests/test_ingredients.py`. Create a new versioned seed when a
change would alter an existing ingredient's identity rather than adding an
alias or correcting metadata.
