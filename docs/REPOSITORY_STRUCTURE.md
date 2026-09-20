# Repository Structure

Annapurna-AI is organized around a Next.js frontend and a FastAPI backend. Keep
changes inside the narrowest capability directory that owns the behavior.

```text
.
├── app/                    Next.js routes and route-level composition
├── components/             Shared React components and UI primitives
├── hooks/                  Reusable client-side state hooks
├── lib/                    Frontend API client and shared utilities
├── backend/
│   ├── alembic/            Ordered database migrations
│   ├── app/
│   │   ├── api/routers/    Thin HTTP endpoints grouped by capability
│   │   ├── core/           Configuration, database, errors, and safety policy
│   │   ├── data/           Versioned local catalogs and evidence
│   │   ├── domain/         Business rules and domain models
│   │   ├── models/         Shared transport and persistence schemas
│   │   ├── repositories/   Database access
│   │   └── services/       Use-case orchestration and external adapters
│   ├── evals/              Offline deterministic planner evaluations
│   └── tests/              Backend behavior and regression tests
├── docs/                   Architecture, operations, and milestone records
└── scripts/                Local setup helpers
```

Start at [Documentation](README.md) for the reader-oriented map. The top-level
`README.md` is the project entry point; `USER_GUIDE.md` is the product manual;
milestone and audit files are historical verification records.

## Frontend Boundaries

- `app` owns route-level data loading and composition for Today, Week, Pantry,
  Shop, Family, Settings, Evidence, and About.
- `components/profile` owns the focused Family form sections.
- `components/ui` contains reusable presentation primitives.
- `hooks` owns reusable client query state.
- `lib/api.ts` is the typed browser boundary for backend requests; `lib/utils.ts`
  contains small shared helpers.

## Backend Boundaries

HTTP handlers validate transport input and delegate work. Services coordinate a
use case. Domain packages own rules and calculations. Repositories own database
access. In normal flow, dependencies point inward:

```text
api routers -> services/domain -> repositories/models
```

The API router modules are grouped by user-facing capability:

- `planning.py`: plan generation, retrieval, locking, replacement, and grocery
  list generation.
- `household.py`: today view, feedback, leftovers, and household commands.
- `pantry.py`: inventory import and quantity transactions.
- `evidence.py`: curated evidence plus optional IFCT and USDA lookup.
- `settings.py` and `health.py`: runtime configuration and health surfaces.

Within `domain`, put reusable business behavior in its owning package. Grocery
compilation therefore lives in `domain/grocery`, while candidate creation,
validation, scoring, and replacement live in `domain/planning`.

## Placement Rules

- Add a frontend route under `app/<route>/page.tsx`; extract shared UI only when
  at least two screens use it or the route becomes difficult to scan.
- Add an endpoint to the matching `api/routers` module and keep persistence out
  of the handler.
- Add business rules to the owning domain package, not to an API or repository
  module.
- Add schema changes through Alembic; do not mutate the schema at application
  startup.
- Keep generated caches, local databases, secrets, and environment-specific
  files out of version control.

## Verification Ownership

- Add backend behavior regressions to `backend/tests`.
- Add deterministic planner quality scenarios to `backend/evals/scenarios` only
  when the assertion is an invariant rather than an exact meal title.
- Run frontend lint and build checks for route or component changes.
- Update the user guide when a visible workflow changes and update architecture
  documents when a dependency boundary moves.
