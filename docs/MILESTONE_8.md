# Milestone 8: Meal Replacement and Locks

> Historical implementation record. This milestone is complete; intermediate
> test counts and next-step notes are preserved for traceability. See
> [Phase Completion](PHASE_COMPLETION.md) for current status.

## Baseline

- Backend tests: 65 passed.
- Backend Ruff, frontend ESLint, TypeScript, and production build: passed.

## Files changed

- Locked meal field, replacement service/models, plan repository update method,
  and two plan-slot API routes.
- Week meal controls and browser API methods.
- Replacement regression test and architecture/product documentation.

## Architecture changes

- `MealReplacementService` patches only the selected slot in the latest local
  plan snapshot.
- Alternatives are deterministically generated, hard-constraint validated, and
  scored with saved preferences and current pantry.
- The grocery compiler runs immediately after replacement.

## Behavior changes

- Meals can be locked or unlocked from Week.
- Locked meals reject replacement with HTTP 409.
- Replacing a meal preserves every other slot and existing locks.
- Week, Today, and Shop refresh after lock or replacement changes.

## Tests added

- Locked-slot conflict.
- One-slot-only replacement and preservation of the other 20 meals.
- Locked meal survival across another slot replacement.
- Grocery response persistence and recalculation after replacement.

## Tests run

- `py -m pytest -q`: 66 passed.
- `py -m ruff check .`: passed.
- `node node_modules\\eslint\\bin\\eslint.js .`: passed.
- `node node_modules\\typescript\\bin\\tsc --noEmit`: passed.
- `node node_modules\\next\\dist\\bin\\next build`: passed.

## Remaining risks

- Replacement uses a small deterministic Telugu/Andhra alternative catalog;
  conversational replacement notes are stored as input but not interpreted.
- The latest plan snapshot is updated in place so existing execution references
  remain valid; detailed replacement history is stored inside that snapshot.

## Historical next step

Milestone 9: AI evaluation scenarios, broader regression coverage, request
correlation, and bounded LLM resilience.
