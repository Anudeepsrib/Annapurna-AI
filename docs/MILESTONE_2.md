# Milestone 2: Ingredient and Unit Normalization

## Baseline

- Backend tests: 17 passed.
- Backend Ruff: passed.

## Files changed

- Ingredient domain models, deterministic normalizer, unit handling, and JSON
  ontology seed.
- Grocery/pantry identity matching in `PlanService`.
- Ingredient regression tests and architecture/product documentation.

## Architecture changes

- Canonical ingredient identity now lives in `domain/ingredients`.
- The ontology remains local, versioned, and file-backed; no database table or
  embedding service was introduced.
- Quantities use `Decimal` and typed units with explicit conversion boundaries.

## Behavior changes

- Common English, Indian, transliterated Telugu, and selected Telugu-script
  ingredient names resolve to stable canonical IDs.
- Grocery merging and pantry matching use canonical identity.
- Unknown and ambiguous ingredients remain explicit instead of being guessed.
- Cross-dimension and package conversions fail rather than fabricating values.

## Tests added

- Ontology size and identity integrity.
- Canonical, alias, Telugu, plural, descriptor, fuzzy, unknown, and ambiguous
  normalization.
- Required units, parsing, 2 kg/2000 g conversion, and invalid conversions.
- End-to-end pantry alias reconciliation in generated grocery output.

## Tests run

- `pytest -q`: 44 passed.
- `ruff check .`: passed.
- `python -m compileall app`: passed.
- `alembic upgrade head` plus `alembic check`: passed with no schema drift.
- `eslint .`: passed using the repository-local ESLint entrypoint.
- `tsc --noEmit`: passed using the repository-local TypeScript entrypoint.
- `next build`: passed; all application routes were generated successfully.

## Remaining risks

- Approximate shelf-life values are planning hints and are not food-safety
  predictions.
- Ingredient-specific density conversions are intentionally unsupported.

## Next milestone

Milestone 3: structured Pantry V2, backend free-text parsing, quantity-aware
pantry reconciliation, and lightweight pantry transactions.
