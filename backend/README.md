# Annapurna-AI Backend

FastAPI backend for local-first meal planning.

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../env.example .env
alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Windows activation:

```powershell
.\venv\Scripts\Activate.ps1
```

Run `alembic upgrade head` after pulling schema changes. The first migration
upgrades an existing local `mealplan` table in place and preserves saved plans.

## Endpoints

- `GET /health`
- `GET /api/v1/health`
- `POST /api/v1/generate-plan`
- `GET /api/v1/plan`
- `GET /api/v1/grocery-list`
- `GET /api/v1/today`
- `POST /api/v1/today/{day}/{meal_type}/status`
- `POST /api/v1/today/{day}/{meal_type}/feedback`
- `GET /api/v1/leftovers`
- `GET /api/v1/pantry`
- `POST /api/v1/pantry/import`
- `POST /api/v1/pantry/{item_id}/transactions`
- `GET /api/v1/pantry/{item_id}/transactions`
- `GET /api/v1/evidence/{topic}`
- `GET /api/v1/mcp/ifct/search?query=rice`
- `GET /api/v1/mcp/usda/search?query=rice`

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

## Planner Pipeline

`PlanService` coordinates structured pantry context, compiled constraints,
candidate generation, validation, scoring, grocery compilation, and plan
persistence. The candidate planner may return multiple plans, but only
schema-valid, hard-constraint-compliant candidates are ranked. If the local LLM
is unavailable or all candidates fail validation, the deterministic fallback
planner supplies the plan. Grocery quantities remain unresolved when recipes do
not provide trustworthy amounts.

## Safety

This backend provides general wellness planning only. It validates LLM output
before saving and applies guardrails for medical-condition, pregnancy, kidney
disease, severe allergy, pediatric, medication-interaction, eating-disorder, and
extreme weight-loss prompts.
