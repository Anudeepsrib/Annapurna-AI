# Milestone 6: Pantry and Shopping Experience

> Historical implementation record. This milestone is complete; intermediate
> test counts and next-step notes are preserved for traceability. See
> [Phase Completion](PHASE_COMPLETION.md) for current status.

## Baseline

- Backend tests: 63 passed.
- Backend Ruff, frontend ESLint, TypeScript, and production build: passed.

## Files changed

- Structured pantry page and browser API types/client methods.
- Explainable shopping-list screen and primary household navigation.
- Household, family-member, pantry, and constraint profile components.
- Product and architecture documentation.

## Architecture changes

- `/pantry` reads and imports the backend-owned structured inventory through
  TanStack Query.
- The profile page coordinates state while focused components own section UI.
- Pantry parsing remains exclusively server-side.

## Behavior changes

- Households can view inventory by pantry, refrigerator, and freezer; see
  expiry, open, category, and unresolved-name states; and import more stock.
- The Shop screen distinguishes buyable items from stock already at home and
  explains every pantry deduction.
- Print, native share, clipboard fallback, and useful shopping summaries work.
- Navigation now exposes Week, Pantry, Shop, and Family as primary destinations.

## Tests added

- No new browser test framework was introduced. Static route generation,
  TypeScript, and ESLint cover the new frontend paths.

## Tests run

- `py -m pytest -q`: 63 passed.
- `py -m ruff check .`: passed.
- `node node_modules\\eslint\\bin\\eslint.js .`: passed.
- `node node_modules\\typescript\\bin\\tsc --noEmit`: passed.
- `node node_modules\\next\\dist\\bin\\next build`: passed, including `/pantry`.

## Remaining risks

- Pantry stock can be imported and reviewed, but transaction controls remain a
  backend/API capability rather than a dense mobile UI.
- Shopping checklist state is intentionally session-local.

## Historical next step

Milestone 7: `/today`, meal execution states, leftovers, and feedback.
