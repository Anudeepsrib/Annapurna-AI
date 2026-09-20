# Annapurna-AI Backend

FastAPI backend for local-first meal planning.

## Run

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp ../env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item ..\env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Run `python -m alembic upgrade head` after pulling schema changes. The first migration
upgrades an existing local `mealplan` table in place and preserves saved plans.

## Source Layout

- `app/api/routers`: thin HTTP handlers grouped by capability.
- `app/domain`: business rules grouped by household, grocery, pantry, planning,
  ingredient, recipe, and feedback domains.
- `app/services`: application orchestration and external-service adapters.
- `app/repositories`: persistence queries and updates.
- `app/models`: shared API and database schemas.
- `app/data`: versioned local evidence, ingredient, recipe, and sample data.
- `tests`: behavior and regression tests; `evals`: deterministic planner quality
  checks.

See `../docs/REPOSITORY_STRUCTURE.md` for the full dependency guide.

## Endpoints

- `GET /health`
- `GET /api/v1/health`
- `POST /api/v1/generate-plan`
- `GET /api/v1/plan`
- `POST /api/v1/plan/{day}/{meal_type}/lock`
- `POST /api/v1/plan/{day}/{meal_type}/replace`
- `POST /api/v1/plan/{day}/regenerate`
- `GET /api/v1/grocery-list`
- `GET /api/v1/today`
- `POST /api/v1/today/{day}/{meal_type}/status`
- `POST /api/v1/today/{day}/{meal_type}/feedback`
- `GET /api/v1/leftovers`
- `PATCH /api/v1/leftovers/{leftover_id}`
- `POST /api/v1/leftovers/{leftover_id}/use/{day}/{meal_type}`
- `POST /api/v1/commands`
- `GET /api/v1/pantry`
- `POST /api/v1/pantry/import`
- `POST /api/v1/pantry/{item_id}/transactions`
- `GET /api/v1/pantry/{item_id}/transactions`
- `GET /api/v1/evidence/{topic}`
- `GET /api/v1/mcp/ifct/search?query=rice`
- `GET /api/v1/mcp/usda/search?query=rice`
- `GET /api/v1/settings/`
- `POST /api/v1/settings/test-llm`
- `GET /api/v1/settings/models`

Interactive OpenAPI documentation is available at `GET /docs` while the
backend is running. Route implementations live in `app/api/routers`; public
paths remain composed by `app/api/routes.py`.

## Privacy Defaults

- SQLite is local.
- Ollama is the default LLM provider.
- USDA and PubMed are disabled by default.
- `ENABLE_EXTERNAL_NETWORK=false` blocks optional fetchers.
- `ENABLE_EXTERNAL_NETWORK=false` blocks non-local LLM endpoints.
- Family profile inputs use role labels, age groups, appetite bands, and dietary
  tags instead of legal names, exact ages, weights, or diagnoses.
- Pantry inventory is stored locally with the generated plan context and used to
  optimize grocery output.
- Health endpoints do not return API keys, database paths, or stack traces.
- Request logs omit prompt and household content; each response includes an
  `X-Request-ID` that is also present in structured error envelopes.

## Plan Request Shape

```json
{
  "householdSize": "3",
  "spiceLevel": "medium",
  "dietary": "vegetarian Andhra home cooking",
  "allergies": ["peanut"],
  "familyProfiles": [
    {
      "label": "Adult cook",
      "ageGroup": "adult",
      "appetite": "regular",
      "dietaryTags": ["prefers rice lunch"],
      "privacyScope": "local_device_only"
    }
  ],
  "pantryInventory": [
    {
      "name": "rice",
      "quantity": "5 kg",
      "category": "grains",
      "expiresWithinDays": 30
    }
  ],
  "pantryText": "rice - 5 kg\nspinach - 1 bunch - use within 2 days",
  "teluguAndhraConstraints": [
    "vegetarian",
    "no_egg",
    "andhra_telugu_style",
    "rice_based_lunch",
    "pappu_or_dal_daily"
  ],
  "preferences": {
    "riceLunchPreference": true,
    "dalMealsPerWeek": 5,
    "fermentedBreakfasts": "prefer",
    "repetitionTolerance": "low",
    "pantryUtilizationPreference": "high"
  }
}
```

`pantryText` is the preferred input for the current text-entry UI and is parsed
authoritatively by the backend. Existing clients may continue sending
`pantryInventory`; if both are provided, `pantryText` takes precedence.
Legacy Telugu/Andhra flags remain accepted. The backend compiles them into
typed hard constraints and soft preferences; explicit `preferences` values
override their corresponding legacy soft defaults.

`POST /api/v1/generate-plan` accepts an optional `Idempotency-Key` header (up to
128 characters). Repeating the same request/key pair returns the original
result. Reusing a key with different input returns `IDEMPOTENCY_CONFLICT`.

## Planner Pipeline

`PlanService` coordinates structured pantry context, compiled constraints,
candidate generation, validation, scoring, grocery compilation, and plan
persistence. The candidate planner may return multiple plans, but only
schema-valid, hard-constraint-compliant candidates are ranked. If the local LLM
is unavailable or all candidates fail validation, the deterministic fallback
planner supplies the plan. Grocery quantities remain unresolved when recipes do
not provide trustworthy amounts.

Model calls use `LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES`,
`LLM_CIRCUIT_BREAKER_FAILURES`, and `LLM_CIRCUIT_BREAKER_SECONDS`. The defaults
bound failures to one retry and open a short in-process circuit before the
deterministic fallback path.

Run deterministic, network-free planner evaluations separately from unit tests:

```bash
python -m evals.run_evals
```

## Development Checks

Run from `backend` with the virtual environment active:

```bash
python -m ruff check .
python -m pytest -q
python -m evals.run_evals
python -m alembic check
```

The current suite has 78 backend tests and three offline planning scenarios.
Milestone documents keep their historical counts, so lower numbers in those
records are not current regressions.

## Household Commands

Commands are parsed deterministically into validated actions; an LLM never
mutates storage directly. Supported examples include:

- `Use the spinach tomorrow`
- `We have 3 guests Saturday`
- `Replace Thursday dinner with paneer`
- `Make Friday dinner easier`
- `Don't buy rice this week`
- `Add dish soap - 1 bottle to the shopping list`

Feedback uses transparent weights: `LIKED` and `WOULD_REPEAT` increase a meal
title's later ranking signal; negative, spice, and effort signals reduce it.

## Safety

This backend provides general wellness planning only. It validates LLM output
before saving and applies guardrails for medical-condition, pregnancy, kidney
disease, severe allergy, pediatric, medication-interaction, eating-disorder, and
extreme weight-loss prompts.

See the repository [User Guide](../docs/USER_GUIDE.md) for browser workflows and
[Architecture](../ARCHITECTURE.md) for system boundaries.
