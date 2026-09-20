# Annapurna-AI

Annapurna-AI is a local-first, culturally aware planning app for Andhra Telugu
vegetarian home cooking. It uses FastAPI, SQLite, LiteLLM/Ollama, and Next.js to
generate weekly meal plans, pantry-aware grocery lists, and privacy-preserving
family planning context while keeping local data on your machine by default.

This is a privacy-aware reference implementation for general wellness planning.
It does not provide medical advice, diagnosis, treatment, or clinical nutrition
plans.

## What Stays Local

- Meal plans and grocery lists are stored in local SQLite.
- Family profiles use role labels, age groups, appetite bands, and dietary tags
  instead of legal names, exact ages, weights, or diagnoses.
- Pantry inventory and Telugu/Andhra dietary constraints are stored with the
  generated plan context locally by default.
- The default LLM endpoint is local Ollama at `http://localhost:11434`.
- USDA and PubMed fetchers are disabled by default.
- No analytics, telemetry, Sentry, PostHog, or LangSmith hooks are included.

See [LOCAL_FIRST.md](LOCAL_FIRST.md) for the full privacy posture.
See [docs/INGREDIENT_ONTOLOGY.md](docs/INGREDIENT_ONTOLOGY.md) for canonical
ingredient identity and unit-conversion behavior.
See [docs/LOCAL_FIRST_PRODUCT_REFRAME.md](docs/LOCAL_FIRST_PRODUCT_REFRAME.md)
for the PM and privacy-by-design reframe.
See [docs/PHASE_COMPLETION.md](docs/PHASE_COMPLETION.md) for the complete
Phase 1–30 implementation map and edge-case coverage.
See [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md) for the source
layout and dependency boundaries.
For day-to-day use, start with the [User Guide](docs/USER_GUIDE.md). The full
documentation index is in [docs/README.md](docs/README.md).

## Product Capabilities

- Privacy-preserving family profiles with role labels, age bands, appetite, and
  scoped dietary tags.
- Pantry inventory intake with quantity and expiry hints.
- Grocery optimization that separates pantry-first items, buy/replenish items,
  and pantry items to use soon.
- Telugu/Andhra dietary rules for vegetarian, no egg, rice-based lunch, daily
  pappu/dal, fermented breakfasts, child-friendly spice, and festival no
  onion/garlic planning.
- Rule-based validation tests that reject malformed model output and cultural
  constraint violations before saving.
- A local ontology of Telugu/South Indian staples with deterministic alias,
  regional-name, quantity, and unit normalization.
- Structured pantry inventory with server-side free-text import, expiry and
  storage metadata, quantity transactions, and stale-update protection.
- Deterministic hard-constraint compilation and validation, with typed soft
  preferences and internal heuristic plan ranking.
- A modular planning pipeline with LLM candidate generation, deterministic
  fallback, validation/ranking, and extracted grocery compilation.
- Household navigation for Week, Pantry, Shop, and Family, including a
  structured pantry screen and explainable pantry-to-shopping deductions.
- A Today workflow for cooked/skipped/leftover/ate-out outcomes, quick meal
  feedback, active leftovers, expiring pantry items, and missing ingredients.
- Per-meal locking and deterministic single-slot replacement with immediate
  grocery recalculation from current pantry stock.
- Durable plan-generation idempotency, request correlation IDs, stable API
  error codes, and bounded local-LLM retries with deterministic fallback.
- Offline invariant evaluations for seven-day shape, hard dietary constraints,
  allergy exclusions, and preference compilation.
- A curated typed recipe catalog with quantified ingredients, pantry quantity
  reconciliation, minimum-stock replenishment, manual list items, shopping
  categories, and non-binding store-affinity hints.
- Transparent feedback-aware ranking, full/day regeneration that preserves
  locked meals, editable reusable leftovers, and validated household commands.
- Local-vs-cloud model boundary: non-local LLM endpoints require
  `ENABLE_EXTERNAL_NETWORK=true`.

## Screenshots

Screenshots are stored in [docs/screenshots](docs/screenshots).

![Profile privacy and pantry intake](docs/screenshots/profile-privacy-pantry.png)

![Pantry-first grocery optimization](docs/screenshots/grocery-optimization.png)

## Documentation

- [User Guide](docs/USER_GUIDE.md): household workflows, backups, privacy, and
  troubleshooting.
- [Local Setup](LOCAL_SETUP.md): installation, startup, verification, Docker,
  and upgrades.
- [Documentation Index](docs/README.md): architecture, domain references,
  evaluations, and historical delivery records.
- [Backend Guide](backend/README.md): API routes, request shape, and development
  checks.

## Sample Plans

See [docs/SAMPLE_MEAL_PLANS.md](docs/SAMPLE_MEAL_PLANS.md) and
[backend/app/data/sample_meal_plans/andhra_telugu_family_week.json](backend/app/data/sample_meal_plans/andhra_telugu_family_week.json).

## Tech Stack

| Area | Version / Tooling |
| --- | --- |
| Frontend | Next.js 16.3.5, React 19.2.3, TypeScript, Tailwind CSS v4 |
| UI | Radix UI, lucide-react, TanStack Query |
| Backend | FastAPI, SQLModel, SQLite, aiosqlite |
| LLM | LiteLLM with local Ollama by default |
| Quality | Ruff, Pytest, offline planning evals, ESLint 9, dependency/secret audits |
| Containers | Docker Compose with a backend service and optional Ollama profile |

## Quick Start

Prerequisites: Python 3.11 or newer, Node.js 20 or newer, and Ollama. For an
expanded first-time setup and verification flow, see [LOCAL_SETUP.md](LOCAL_SETUP.md).

### 1. Install Ollama

Install Ollama from [https://ollama.com](https://ollama.com), then pull the
default model:

```bash
ollama pull llama3.2:latest
```

### 2. Clone

```bash
git clone https://github.com/Anudeepsrib/Annapurna-AI.git
cd Annapurna-AI
```

### 3. Backend

macOS/Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../env.example .env
alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item ..\env.example .env
alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Frontend

In a second terminal:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Setup Scripts

The setup helpers are optional:

```bash
bash scripts/setup.sh
```

```powershell
.\scripts\setup.ps1
```

The Windows command is `.\scripts\setup.ps1`.

## Docker Compose

Backend with host Ollama:

```bash
docker compose up --build backend
```

Optional Ollama container profile:

```bash
docker compose --profile ollama up --build
```

The backend container applies pending Alembic migrations before starting the API.

If you use the Ollama profile, pull a model into that container before
generating plans:

```bash
docker compose --profile ollama exec ollama ollama pull llama3.2:latest
```

## Configuration

Copy `env.example` to `backend/.env` for backend settings. Defaults are local:

```env
APP_ENV=development
DEBUG=false
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DATABASE_URL=sqlite+aiosqlite:///./annapurna.db
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:latest
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=1
LLM_CIRCUIT_BREAKER_FAILURES=3
LLM_CIRCUIT_BREAKER_SECONDS=60
ENABLE_EXTERNAL_NETWORK=false
ENABLE_USDA=false
ENABLE_PUBMED=false
```

Use `.env.local` only for frontend settings such as `BACKEND_URL` or
`NEXT_PUBLIC_API_BASE_PATH`. Do not put secrets in `NEXT_PUBLIC_*` variables.

## Optional External Fetchers

USDA and PubMed are off by default. To enable either fetcher, you must set:

```env
ENABLE_EXTERNAL_NETWORK=true
```

USDA also requires `ENABLE_USDA=true` and `USDA_API_KEY`.
PubMed also requires `ENABLE_PUBMED=true` and `PUBMED_EMAIL`.

## Local vs Cloud Models

Local model mode is the default:

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
ENABLE_EXTERNAL_NETWORK=false
```

External model mode is opt-in. If `LLM_BASE_URL` points to a non-local host,
the backend requires:

```env
ENABLE_EXTERNAL_NETWORK=true
```

In external mode, family profile labels, pantry inventory, allergies, and
dietary prompts may leave the machine as model prompt data. Keep local mode for
private household planning.

## Safety Boundaries

Annapurna-AI returns general wellness guidance only. It is not a medical device,
diagnosis tool, treatment planner, or clinical nutrition system. Prompts involving diabetes,
pregnancy, kidney disease, eating disorders, severe allergies, epilepsy
medication interactions, pediatric diets, or extreme weight-loss goals trigger
guardrails advising review with a qualified clinician or registered dietitian.

Nutrition estimates are approximate. The app does not claim HIPAA, GDPR,
medical, or clinical compliance.

## Validation

Backend:

```bash
python -m compileall backend/app
cd backend
pip install -r requirements.txt
pip check
pytest
python -m evals.run_evals
ruff check .
alembic upgrade head
alembic check
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
npm install
npm run lint
npm run build
npm audit
```

Docker:

```bash
docker compose config
docker compose build
```

## Troubleshooting

Ollama not running:

```bash
ollama list
ollama serve
```

Model not pulled:

```bash
ollama pull llama3.2:latest
```

Invalid LLM JSON:

The backend validates model output. If the model returns malformed JSON or
missing fields, the app uses a deterministic fallback plan and marks the source
status as `fallback_invalid_llm_json`.

SQLite permission issue:

Check that the backend process can write to `backend/annapurna.db` or the Docker
volume mounted at `/app/data`.

CORS issue:

Set `CORS_ORIGINS` in `backend/.env`, for example:

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Offline backend from frontend:

Confirm FastAPI is listening at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).
