# Milestone 3: Structured Pantry and Transactions

## Baseline

- Backend tests: 44 passed.
- Backend Ruff: passed.

## Files changed

- Pantry SQLModel records, Alembic migration, domain schemas/service, repository,
  API routes, plan/grocery integration, frontend raw-text submission, tests, and
  product/architecture documentation.

## Architecture changes

- `PantryService` owns server-side parsing, normalization, inventory rules, and
  transaction calculations.
- `PantryRepository` owns structured inventory persistence and atomic
  version-checked mutations.
- Pantry items and transactions are separate local SQLite tables.

## Behavior changes

- Raw profile pantry text is parsed and categorized by the backend.
- Legacy `pantryInventory` requests remain supported.
- Canonical aliases upsert one inventory identity; unknown names and quantities
  are retained without guessing.
- Current transaction-adjusted inventory drives grocery refreshes.
- Expired and zero-quantity stock is excluded from pantry availability.

## Tests added

- Raw-text parsing and structured persistence.
- Alias deduplication and unresolved quantity preservation.
- Same-dimension transaction conversion and event history.
- Insufficient stock, incompatible units, and stale version conflicts.
- Expired/zero stock and post-transaction grocery reconciliation.
- Legacy structured field round trips and migration table creation.

## Tests run

- `py -m pytest -q`: 51 passed.
- `py -m ruff check .`: passed.
- `py -m compileall app`: passed.
- `alembic upgrade head`: passed from an empty SQLite database.
- `alembic check`: no new upgrade operations detected.
- `node node_modules\\eslint\\bin\\eslint.js .`: passed.
- `node node_modules\\typescript\\bin\\tsc --noEmit`: passed.
- `node node_modules\\next\\dist\\bin\\next build`: passed.

## Remaining risks

- Recipe ingredient requirements remain unquantified, so exact pantry
  subtraction is deferred rather than fabricated.
- Imports upsert submitted items but do not delete unmentioned inventory.

## Next milestone

Milestone 4: deterministic hard-constraint compilation, typed soft preferences,
plan validation, and heuristic plan scoring.
