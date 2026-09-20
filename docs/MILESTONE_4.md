# Milestone 4: Constraints, Preferences, Validation, and Scoring

## Baseline

- Backend tests: 51 passed.
- Backend Ruff: passed.
- Frontend ESLint, TypeScript, and production build: passed.

## Files changed

- Planning-domain constraint, preference, validation, and scoring modules.
- Plan request, prompt, orchestration, and TypeScript request types.
- Planner regression tests and architecture/API documentation.

## Architecture changes

- `ConstraintEngine` adapts existing request fields into typed hard constraints
  and soft preferences.
- `PlanValidator` owns schema and hard-constraint validation independently of
  the LLM.
- `PlanScorer` owns deterministic candidate ranking with injectable heuristic
  weights. Numeric scores remain internal.

## Behavior changes

- Vegetarian, egg-free, allergen, no-onion, and no-garlic rules are enforced as
  hard constraints with word-boundary matching.
- Rice lunches, dal frequency, fermented breakfasts, repetition tolerance, and
  pantry/reuse preferences influence ranking rather than validity.
- Existing `teluguAndhraConstraints` requests continue to work, while clients
  may provide an optional typed `preferences` object.
- Saved plan snapshots include the compiled rules used for generation.

## Tests added

- Legacy hard-rule and soft-preference compilation.
- Chicken, egg, onion, and garlic rejection.
- Eggplant word-boundary regression and soft-preference non-rejection.
- Pantry/expiry/variety scoring and deterministic selection.
- Vegetarian API fallback and dairy-allergen alias handling.

## Tests run

- `py -m pytest -q`: 60 passed.
- `py -m ruff check .`: passed.
- `py -m compileall app`: passed.
- `node node_modules\\eslint\\bin\\eslint.js .`: passed.
- `node node_modules\\typescript\\bin\\tsc --noEmit`: passed.
- `node node_modules\\next\\dist\\bin\\next build`: passed.

## Remaining risks

- Preparation effort, cooking time, and leftovers are typed but cannot affect
  ranking until recipes and meal execution expose those facts.
- Scoring weights are product heuristics, not scientifically validated values.

## Next milestone

Milestone 5: extract candidate planning, deterministic fallback, and grocery
compilation so `PlanService` only coordinates the workflow.
