# Planner Pipeline

`PlanService` coordinates generation; deterministic domain components decide
what is valid, how candidates rank, and how pantry stock changes the shopping
list.

```text
PlanRequest + current pantry + saved feedback/locks
        |
        v
Idempotency lookup -------- matching key/result -> replay
        |
        v
ConstraintEngine -> typed hard constraints + soft preferences
        |
        v
CandidatePlanner -> configured local LLM by default
        |
        v
PlanValidator -> discard malformed or hard-rule-invalid candidates
        |
        v
PlanScorer -> rank valid candidates with preferences, pantry, and feedback
        |
        v
Preserve compatible locked slots
        |
        v
GroceryCompiler -> recipe requirements - usable pantry + manual/minimum stock
        |
        v
PlanRepository -> plan, provenance, compiled context, and idempotent result
```

Safety guardrail requests, unavailable/timed-out model calls, and zero valid
candidates use `FallbackPlanner`. Its result passes through the same validation,
grocery, provenance, and persistence boundaries. Fallback is a supported result,
not an unvalidated escape path.

## Responsibility Boundaries

- `PlanService` coordinates the workflow, idempotency, saved context, source
  status, and persistence.
- `CandidatePlanner` calls the configured model and extracts one or more
  candidate payloads.
- `ConstraintEngine` compiles hard constraints and soft preferences.
- `PlanValidator` enforces the response schema and hard dietary constraints.
- `PlanScorer` applies configurable pantry, expiry, preference, variety,
  repetition, reuse, waste, and feedback heuristics. Scores remain internal.
- `FallbackPlanner` builds the local deterministic seven-day plan.
- `GroceryCompiler`, in `app/domain/grocery`, merges canonical ingredients,
  quantified recipe requirements, usable pantry stock, minimum-stock targets,
  manual items, and use-soon requests.
- `RecipeCatalog` loads and validates the versioned local recipe data.
- `PlanRepository` persists plan snapshots, component versions, generation
  provenance, and idempotency records.

Model output never owns allergies, prohibited ingredients, unit conversion,
pantry identity, expiry, locks, or grocery reconciliation. Unknown quantities
remain explicit rather than being fabricated.

## Replacement and Day Refresh

`MealReplacementService` handles targeted changes without running the whole
generation pipeline. It rejects locked slots, chooses deterministic catalog
alternatives, validates and scores the changed plan, recalculates groceries, and
updates the latest snapshot. Day refresh applies the same process to unlocked
slots only.

## Versioning and Observability

New generations persist the prompt, candidate planner, fallback planner,
validator, and grocery compiler versions with provider/model labels, source
status, timestamp, generation ID, and fallback flag. The API does not persist or
return chain-of-thought.

Requests receive an `X-Request-ID`; logs record route metadata and component
labels but omit prompts, household profiles, pantry contents, secrets, and query
strings. See [Architecture](../ARCHITECTURE.md) for the full runtime boundary.
