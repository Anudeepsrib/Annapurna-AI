# Milestone 7: Today, Execution, Leftovers, and Feedback

## Baseline

- Backend tests: 63 passed.
- Backend Ruff, frontend ESLint, TypeScript, and production build: passed.

## Files changed

- Meal execution, feedback, and leftover database records and migration.
- Feedback repository, Today domain models/service, and versioned API routes.
- `/today` page, client types/actions, and Today navigation.
- Regression tests and product/architecture documentation.

## Architecture changes

- `TodayService` composes the latest plan, current pantry, grocery deductions,
  execution state, leftovers, and feedback without invoking the LLM.
- `FeedbackRepository` owns lightweight household activity persistence.
- Migration `0003_household_activity` adds three local tables with idempotent
  meal-slot and feedback constraints.

## Behavior changes

- Today shows breakfast, lunch, dinner, preparation ingredients, missing stock,
  expiring pantry items, and active leftovers.
- Meals can be marked cooked, skipped, saved as leftovers, or eaten outside.
- Households can record liked, too-spicy, too-much-work, and would-repeat
  signals; duplicate signals are idempotent.
- Marking a meal as leftover creates or refreshes a lightweight two-day
  leftover record with one serving by default.

## Tests added

- End-to-end Today composition, status updates, leftover creation, idempotent
  feedback, expiry visibility, and leftover retrieval.
- Actionable Today response when no plan exists.
- Legacy database upgrade now verifies all Milestone 7 tables and revision.

## Tests run

- `py -m pytest -q`: 65 passed.
- `py -m ruff check .`: passed.
- `py -m compileall app`: passed.
- `node node_modules\\eslint\\bin\\eslint.js .`: passed.
- `node node_modules\\typescript\\bin\\tsc --noEmit`: passed.
- `node node_modules\\next\\dist\\bin\\next build`: passed, including `/today`.
- `git diff --check`: passed.

## Remaining risks

- Leftover safety uses user-visible `usableUntil` dates and a simple two-day
  default; it is not a food-safety prediction.
- Feedback is recorded transparently but does not influence ranking until a
  later planner iteration.
- Meal status does not automatically subtract pantry quantities because recipe
  amounts remain unstructured.

## Next milestone

Milestone 8 would add partial meal replacement, locked meals, and grocery
recalculation. It was not started in this run.
