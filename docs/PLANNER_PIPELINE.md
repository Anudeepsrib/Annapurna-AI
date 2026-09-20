# Planner Pipeline

The implemented weekly planning flow is:

```text
PlanRequest + current pantry
        |
        v
ConstraintEngine
        |
        v
CandidatePlanner (local LLM by default)
        |
        v
PlanValidator -- discard invalid candidates
        |
        v
PlanScorer -- select the best valid candidate
        |
        v
GroceryCompiler
        |
        v
PlanRepository
```

Safety guardrail requests and candidate-generation failures use the
`FallbackPlanner`, then pass through the same deterministic validator before
grocery compilation and persistence.

## Responsibility boundaries

- `PlanService` coordinates the workflow and source-status handling.
- `CandidatePlanner` calls the configured LLM and extracts candidate payloads.
- `ConstraintEngine` compiles hard constraints and soft preferences.
- `PlanValidator` enforces schema and hard constraints.
- `PlanScorer` applies configurable ranking heuristics to valid candidates.
- `FallbackPlanner` builds the local deterministic seven-day plan.
- `GroceryCompiler` merges canonical ingredients and reconciles usable pantry
  stock without inventing recipe quantities.
- `PlanRepository` persists versioned plan snapshots and provenance.

Model output never bypasses validation. A candidate may influence meal text,
but it does not own allergies, prohibited ingredients, unit conversion, pantry
identity, expiry, or grocery reconciliation.

The scorer is an internal ranking heuristic. Its numeric score is not returned
to users and is not presented as a scientific nutrition measure.
