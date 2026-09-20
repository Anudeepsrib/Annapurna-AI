# Offline Planning Evaluations

The evaluation suite checks product invariants without calling an LLM or network
service. Run it from `backend`:

```bash
python -m evals.run_evals
```

Scenarios are versioned in `evals/scenarios/planning_invariants.json`. Each
scenario becomes a typed `PlanRequest`, compiles hard constraints and soft
preferences, builds the deterministic fallback, validates the complete week,
and scores it. The gate checks:

- exactly seven schema-valid days;
- vegetarian, egg, onion/garlic, and allergen exclusions with word boundaries;
- deterministic preference compilation such as child-friendly mild spice;
- successful scoring with pantry and expiry context.

The suite intentionally avoids exact meal-title assertions. Meal wording may
evolve while safety, dietary, shape, and deterministic behavior remain stable.
CI runs this gate separately from Pytest so an invariant regression is visible
as an evaluation failure.

The current three scenarios cover a vegetarian/no-egg festival week, a dairy
allergy, and a pantry-aware vegetarian week. Add a scenario only for a stable
product invariant; use backend tests for endpoint, repository, and error-path
behavior.
