# Annapurna-AI User Guide

Annapurna-AI helps an Andhra Telugu household plan a vegetarian week, use pantry
stock first, track daily meal outcomes, and build an explainable shopping list.
It runs without accounts or analytics and uses a local Ollama model by default.

The app provides general wellness meal-planning ideas, not medical advice. Check
every suggestion against your household's allergies and needs. Seek qualified
clinical guidance for medical conditions, pregnancy, pediatric therapeutic
diets, eating disorders, medication interactions, or severe allergies.

## Start the App

Complete the [local setup](../LOCAL_SETUP.md) once. For normal use, keep Ollama
running and open two terminals from the repository root.

Backend on Windows PowerShell:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend on macOS or Linux:

```bash
cd backend
source venv/bin/activate
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend in the second terminal:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The backend health check is
available at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

## Main Navigation

| Screen | Purpose |
| --- | --- |
| Today | Follow today's meals, record outcomes and feedback, manage leftovers, and enter household commands. |
| Week | Review all seven days, lock meals, replace one meal, or refresh a day's unlocked meals. |
| Pantry | Import or review locally stored household inventory. |
| Shop | Check off missing ingredients and review pantry deductions. |
| Family | Enter household context and generate or regenerate the weekly plan. |
| Settings | Inspect the active model, privacy mode, database location, and optional network features. |

## Create Your First Plan

1. Open **Family**.
2. Enter the household size, preferred spice level, allergies, and a short
   dietary description.
3. Describe family members using role labels such as `Adult cook`, `Senior`, or
   `Child`. Use broad age and appetite bands rather than names, exact ages,
   weights, or diagnoses.
4. Enter pantry stock, one item per line.
5. Select the Telugu and Andhra rules that must apply.
6. Choose **Generate Private Weekly Plan**. The app validates the result before
   saving it and opens **Week**.

Example pantry input:

```text
rice - 5 kg
kandi pappu - 1 kg
spinach - 1 bunch - use within 2 days
tamarind - small box
```

Separate allergies with commas. Hard rules such as vegetarian, no egg, and
festival no onion/garlic are enforced after generation. Preferences such as
rice lunches, dal frequency, mild spice, and pantry use guide ranking but do not
override hard rules.

If Ollama is unavailable, times out, or returns invalid output, the app uses a
validated deterministic fallback plan. Check the plan's source and safety notes
rather than assuming every plan came from the configured model.

## Use the Week Screen

- Select a day to see breakfast, lunch, and dinner.
- Choose **Lock** on a meal you want to keep. Locked meals cannot be replaced or
  changed by day refreshes.
- Choose **Replace** to change only that unlocked meal. The shopping list is
  recalculated immediately.
- Choose **Refresh unlocked meals** to regenerate only the selected day's
  unlocked slots.
- Use **Grocery List** for a compact list, or open **Shop** for the full
  pantry-aware checklist.

When you return to **Family** and generate a new plan, compatible locked meals
are preserved. If a lock conflicts with new hard constraints, unlock that meal
before regenerating.

## Keep the Pantry Current

Open **Pantry**, enter one item per line, and choose **Update pantry**. Imports
update matching canonical ingredients and add new ones; they do not delete
items omitted from the import.

The local ingredient dictionary recognizes common English, Indian, and selected
Telugu names. Unknown names are kept as unresolved instead of being guessed.
Numeric weight and volume quantities can be reconciled only within the same
dimension; the app does not invent package conversions or density estimates.

The current Pantry screen supports text import and review. Detailed purchase,
consume, adjust, expire, discard, and restock transactions are available in the
backend API but do not yet have dedicated controls in the browser UI.

## Use Today

**Today** combines the current day's three meals with missing ingredients,
pantry items expiring within five days, and active leftovers.

For each meal, record one of these outcomes:

- **Cooked**
- **Skipped**
- **Saved leftovers**
- **Ate outside**
- **Replaced**

You can also record **Liked**, **Disliked**, **Too spicy**, **Too much work**,
**Would repeat**, or **Would not repeat**. Feedback stays local and influences
later plan ranking through visible heuristic weights; it is not a hidden
machine-learning profile.

Saving leftovers asks for servings and a use-by date. In the Leftovers panel,
choose **Dinner** to assign an item to today's dinner or **Used up** to consume
it. Use-by dates are household reminders, not food-safety predictions.

## Use Household Commands

The command box on **Today** accepts a small, validated set of household
actions. Examples:

- `Use the spinach tomorrow`
- `We have 3 guests Saturday`
- `Replace Thursday dinner with paneer`
- `Make Friday dinner easier`
- `Don't buy rice this week`
- `Add dish soap - 1 bottle to the shopping list`

Commands are parsed deterministically. They do not give an LLM direct access to
the database, and unsupported wording returns an error instead of guessing.

## Shop From the Generated List

The **Shop** screen separates the list into:

- **Use From Pantry First**: usable stock already at home.
- **Buy / Replenish**: missing ingredients or stock below a configured minimum.
- **Pantry Items To Use Soon**: expiring stock not otherwise used by the plan.

Each row explains the deduction, associated meals, and an advisory store type.
Store suggestions are hints only; the app does not connect to a retailer or
place orders. Checkboxes last only for the current browser session. Use
**Print** for a paper/PDF copy or **Share** to open the device share sheet; when
native sharing is unavailable, the app copies the buy list to the clipboard.

## Check Settings and Evidence

**Settings** shows safe configuration fields only. Use **Test Connection** to
check the configured model and **List Available Models** to list local Ollama
models. Configuration controls are read-only in the UI: edit `backend/.env` and
restart the backend to change them.

The Week screen shows curated general-wellness evidence where available. The
standalone `/evidence` page explains the product's evidence principles. USDA
and PubMed access remains off unless explicitly enabled in the environment.

## Protect and Back Up Your Data

With the default configuration, plans, pantry inventory, activity, feedback,
leftovers, and idempotency records live in `backend/annapurna.db`. To back up a
local installation:

1. Stop the backend.
2. Copy `backend/annapurna.db` to a private backup location.
3. Keep `backend/.env` private; it may contain API keys if online features were
   enabled.

Restore by stopping the backend and replacing the database with a compatible
backup, then run `python -m alembic upgrade head` from `backend`. Docker Compose
stores the database in the `annapurna-data` named volume rather than the source
tree.

Do not commit the database, `.env` files, exported household data, or logs.

## Local and External Modes

The default model endpoint is local Ollama at `http://localhost:11434`.
`ENABLE_EXTERNAL_NETWORK=false` also blocks optional USDA and PubMed fetchers
and rejects non-local model endpoints.

If you intentionally enable an external model or fetcher, prompt or search data
may leave the computer. This can include role labels, pantry items, allergies,
and dietary text. See [Local-First Privacy Notes](../LOCAL_FIRST.md) before
changing the network settings.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Frontend says the backend is unavailable | Open `http://127.0.0.1:8000/health`; start FastAPI if it does not return `status: ok`. |
| Model connection fails | Run `ollama list`, start Ollama, and pull `llama3.2:latest` if it is missing. |
| A fallback plan appears | Check Ollama and the Settings connection test. Fallback is expected after unavailable, timed-out, or invalid model output. |
| Pantry item is unresolved | Try a canonical/common name, but keep the original entry if no safe match exists. |
| Shopping quantity says to preserve recipe units | The recipe or pantry quantity could not be converted safely; verify the amount manually. |
| A locked meal will not change | Unlock it before replacement or regeneration. |
| Browser request fails with an error code | Retry once, then note the returned `X-Request-ID` from browser developer tools or backend logs. |
| Database or migration error | Stop the backend, back up the database, activate the backend virtual environment, and run `python -m alembic upgrade head`. |
| Port 3000 or 8000 is occupied | Stop the conflicting process or start that service on another port and update the matching URL/CORS setting. |

For installation failures, use the expanded [README troubleshooting
section](../README.md#troubleshooting). For security or privacy concerns, see
the [Security Policy](../SECURITY.md).

## Known Product Boundaries

- This is a single-household, local-first application without user accounts.
- Nutrition values and shelf-life hints are approximate and are not clinical or
  food-safety determinations.
- The recipe catalog is deliberately small and curated.
- Pantry transactions are API-first; the browser UI focuses on import/review.
- Shopping checklist state is not persisted.
- Retailer affinity is advisory; there is no checkout integration.
- Offline evaluations check deterministic invariants, not subjective taste or
  live-model quality.
