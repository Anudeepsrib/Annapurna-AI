# Milestone 5: Planner Service Extraction

## Baseline

- Milestone 4 backend tests: 60 passed.
- Backend Ruff, Python compilation, frontend ESLint, TypeScript, and production
  build: passed.

## Files changed

- Candidate planner, deterministic fallback planner, and grocery compiler.
- `PlanService` orchestration and versioned saved-plan context.
- Pipeline-specific regression tests and architecture documentation.

## Architecture changes

- `PlanService` now coordinates specialized planning-domain services instead of
  owning JSON parsing, fallback meal construction, and grocery merging.
- `CandidatePlanner` accepts single or multiple model candidates.
- All candidates pass through the deterministic validator; the scorer selects
  only among valid candidates.
- `FallbackPlanner` and `GroceryCompiler` are independently testable services.

## Behavior changes

- Multiple valid model candidates can be ranked using pantry and preference
  context.
- Invalid candidates are discarded; an unavailable model or zero valid
  candidates still produces the deterministic fallback.
- Grocery responses keep the existing API shape and canonical alias matching.
- Generation metadata now identifies `candidate_planner_v2`; saved snapshots
  record fallback and grocery compiler versions.

## Tests added

- Fenced multi-candidate response extraction.
- End-to-end candidate ranking toward expiring pantry stock and variety.
- Extracted grocery compiler alias reconciliation.
- Existing fallback, malformed JSON, constraint, pantry, and grocery regression
  tests continue covering the refactored paths.

## Tests run

- `py -m pytest -q`: 63 passed.
- `py -m ruff check .`: passed.
- `py -m compileall app`: passed.
- `node node_modules\\eslint\\bin\\eslint.js .`: passed.
- `node node_modules\\typescript\\bin\\tsc --noEmit`: passed.
- `node node_modules\\next\\dist\\bin\\next build`: passed.
- `git diff --check`: passed.

## Remaining risks

- The current prompt normally requests one candidate; multi-candidate ranking is
  available when a provider returns the supported `candidates` envelope.
- Recipe ingredients still lack reliable structured amounts, so grocery output
  preserves uncertainty instead of fabricating quantities.

## Next milestone

Milestone 6: add `/pantry`, improve the shopping-list reasoning UI, and split
the large profile screen into focused components.
