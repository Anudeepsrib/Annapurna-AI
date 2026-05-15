# Audit Report

Date: 2026-05-15

## Summary

The repository was audited as a local-first FastAPI, SQLite, LiteLLM/Ollama, and
Next.js meal planner. The main runtime, privacy, safety, Docker, CI, dependency,
and documentation issues were repaired.

## Findings and Fixes

### P0

- Backend runtime and tests referenced missing or obsolete modules. Rewrote
  startup/config paths, removed obsolete `backend/main.py` and `backend/mock_data.py`,
  and added package initializers and pytest config.
- `backend/annapurna.db` was tracked. Removed it from the Git index and added
  ignore rules for local SQLite and generated data.
- Dockerfile and Compose were rewritten into valid, local-only defaults.

### P1

- Privacy claims were too broad. Runtime defaults now block USDA/PubMed unless
  `ENABLE_EXTERNAL_NETWORK=true` and the specific fetcher is configured.
- Google font fetching and Axios were removed from the frontend.
- Wellness and medical guardrails were added for diabetes, pregnancy, kidney
  disease, allergies, eating disorders/extreme weight loss, epilepsy medication
  interactions, and pediatric diets.
- `next lint` was invalid for this Next.js install. The lint script now uses
  `eslint .`.
- CI now runs backend compile, Ruff, Pytest, pip-audit, frontend lint/build, and
  npm high/critical audit.

### P2

- LLM output is schema-validated before saving.
- Malformed/missing LLM JSON falls back to a deterministic validated plan.
- Offline local LLM returns a clear generation-time error without breaking app
  startup.
- Grocery list generation deduplicates ingredients without unsafe unit math.
- Request logging no longer records query strings or dietary free text by default.
- Frontend API calls are centralized and environment-driven.
- Loading, empty, backend-error, and safety-note UI states were added or improved.

### P3

- README, local setup, architecture, security, and local-first docs were updated.
- Package files and environment templates were reformatted for maintainability.

## Files Changed

- Runtime/config: `backend/app/main.py`, `backend/app/core/config.py`,
  `backend/app/core/database.py`, `backend/app/core/exceptions.py`,
  `backend/app/core/safety.py`
- Backend API/services/models: `backend/app/api/routes.py`,
  `backend/app/api/settings.py`, `backend/app/models/db.py`,
  `backend/app/models/schemas.py`, `backend/app/services/*.py`
- Backend tests/config: `backend/tests/conftest.py`, `backend/tests/test_api.py`,
  `backend/pyproject.toml`, `backend/requirements.txt`
- Frontend: `lib/api.ts`, `hooks/use-plan.ts`, `app/**`, `components/**`,
  `next.config.ts`, `package.json`, `package-lock.json`
- Docker/CI/config: `backend/Dockerfile`, `docker-compose.yml`,
  `.github/workflows/ci.yml`, `.gitignore`, `env.example`
- Docs: `README.md`, `LOCAL_FIRST.md`, `SECURITY.md`, `ARCHITECTURE.md`,
  `LOCAL_SETUP.md`, `FIX_LOG.md`, `backend/README.md`, `AUDIT_REPORT.md`
- Removed obsolete/private-risk files: `backend/main.py`, `backend/mock_data.py`,
  `backend/data/evidence/*`, `install.cmd`; de-indexed `backend/annapurna.db`

## Commands Run

| Command | Result |
| --- | --- |
| `rg --files -g '!node_modules' -g '!**/.git/**'` | Passed; repository tree inspected. |
| `rg -n "fetch\|axios\|httpx\|requests\|openai\|anthropic\|google\|azure\|telemetry\|analytics\|sentry\|langsmith\|posthog"` | Passed; external-call surfaces reviewed. |
| `rg -n "(?i)(api[_-]?key\|secret\|token\|password\|BEGIN [A-Z ]*PRIVATE KEY\|sk-[A-Za-z0-9])"` | Passed; no real secrets found, only templates/config names. |
| `python -m compileall backend/app` | Passed. |
| `cd backend && pip install -r requirements.txt` | Passed; global environment reports unrelated resolver warnings. |
| `cd backend && pip check` | Failed due pre-existing global Python package conflicts outside this repo. See remaining risks. |
| `cd backend && pytest` | Passed: 11 tests. |
| `cd backend && ruff check .` | Passed. |
| `cd backend && pip-audit -r requirements.txt` | Passed: no known vulnerabilities found after updating pytest requirement. |
| `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | Passed; server started and `/health` returned safe status. |
| Background local launch for backend and frontend | Passed; backend `/health` returned 200 and frontend returned HTTP 200 at `http://127.0.0.1:3000`. |
| `npm install` | Passed. |
| `npm run lint` | Passed. |
| `npm run build` | Passed. |
| `npm audit` | Failed with 2 moderate Next/PostCSS advisories; no high/critical after fixes. |
| `npm audit --audit-level=high` | Passed. |
| `docker compose config` | Passed. |
| `docker compose build` | Not run successfully because Docker Desktop/Linux engine was not available. |
| `git check-ignore -v --no-index ...` | Passed for `.env`, backend env files, SQLite DBs, generated data, reports, and logs. |

## Privacy Posture

Before:

- A local SQLite database was tracked.
- Runtime docs claimed broad privacy guarantees while frontend Google fonts and
  optional fetchers were not fully explained.
- USDA/PubMed were feature-flagged but not protected by a master external-network
  gate.

After:

- Local DBs, env files, generated plans, caches, logs, reports, and local data
  paths are ignored.
- `backend/annapurna.db` is removed from the Git index.
- Default runtime calls only the local backend and configured local LLM endpoint.
- USDA/PubMed require explicit opt-in and required settings.
- Docs describe local-first behavior and optional external behavior without
  claiming clinical or compliance guarantees.

## Remaining Manual Actions

- Start Docker Desktop and rerun `docker compose build`.
- Pull the local model with `ollama pull llama3.2:latest`.
- Create `backend/.env` from `env.example` for local development.
- Review and commit the staged removal of `backend/annapurna.db`.

## Remaining Risks

- `pip check` fails in this machine's shared global Python install because of
  unrelated packages such as Camelot, LangChain, LlamaIndex, Semantic Kernel, and
  pytest-asyncio. Use a fresh virtual environment or CI for authoritative checks.
- `npm audit` still reports a moderate PostCSS advisory through the latest stable
  Next.js 16.2.6 release. `npm audit --audit-level=high` passes; do not downgrade
  to the suggested Next.js 9 fix.
- Nutrition estimates are placeholders unless a verified nutrition enrichment
  pipeline is added.
- ICMR/IFCT local JSON is small curated reference data, not a complete evidence
  database.
- No browser automation screenshot pass was completed in this environment.

## Recommended Commit Message

```text
Repair local-first runtime, safety guardrails, CI, and docs
```
