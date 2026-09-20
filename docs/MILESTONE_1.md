# Milestone 1: Persistence and Generation Provenance

> Historical implementation record. This milestone is complete; intermediate
> test counts and next-step notes are preserved for traceability. See
> [Phase Completion](PHASE_COMPLETION.md) for current status.

## Baseline

Captured before implementation on 2026-09-19:

- Backend tests: 14 passed.
- Backend Ruff: passed.
- Frontend TypeScript (`tsc --noEmit`): passed.
- Frontend production build: passed.
- Frontend ESLint could not complete because it traversed an inaccessible
  `backend/.pytest_cache`; the frontend config now excludes the backend tree.
- The host's global `npm`/`npx` wrappers point to a missing npm installation.
  Equivalent local Node entrypoints were used without changing dependencies.

## Files changed

- Alembic configuration, the initial compatibility migration, and local/Docker
  startup integration.
- Plan model, generation metadata schema, repository, prompt module, service,
  API route, regression tests, CI, and setup/architecture documentation.

## Architecture changes

- `PlanService` delegates persistence to the concrete `PlanRepository`.
- Planner prompt text and formatting live in versioned `planner_v1`.
- Alembic replaces runtime schema mutation for application startup.
- New plans persist typed generation provenance in one nullable JSON column.

## Behavior changes

- Existing routes and legacy plan payloads remain compatible.
- Generation responses include `generation_metadata`.
- An unavailable LLM now returns and persists a deterministic fallback plan
  instead of making the household workflow unavailable.

## Tests added

- Versioned prompt context regression.
- Repository metadata persistence regression.
- Existing-database Alembic upgrade regression.
- LLM-unavailable deterministic fallback regression.

## Tests run

- `pytest -q`: 17 passed.
- `ruff check .`: passed.
- `python -m compileall app`: passed.
- `alembic upgrade head`: passed against an isolated fresh SQLite database.
- `alembic check`: passed with no schema drift.
- `eslint .`: passed using the repository-local ESLint entrypoint.
- `tsc --noEmit`: passed using the repository-local TypeScript entrypoint.
- `next build`: passed; all application routes were generated successfully.
- `docker compose config`: passed (the sandbox could not read the user's Docker
  client config, which does not affect Compose validation).
- PowerShell parser: `setup.ps1` and `dev.ps1` syntax passed.
- Bash parser: `setup.sh` syntax passed.

## Remaining risks

- Migration downgrade intentionally removes only the added metadata column and
  retains the legacy `mealplan` table to avoid destructive local-data loss.
- Existing installations must run `alembic upgrade head` once before startup.

## Historical next step

Milestone 2 is the ingredient ontology plus deterministic ingredient and unit
normalization. It should begin only after all Milestone 1 checks pass.
