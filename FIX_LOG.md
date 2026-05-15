# Fix Log

This repository was audited and repaired as a local-first FastAPI and Next.js
meal planner.

Current notable fixes:

- Backend settings are centralized in `backend/app/core/config.py`.
- FastAPI exposes safe health endpoints and avoids logging dietary/free-text
  request details.
- Meal-plan LLM output is schema-validated before saving.
- Malformed LLM JSON falls back to a deterministic validated plan.
- Offline Ollama returns a clear generation-time error without blocking app
  startup.
- USDA and PubMed fetchers are disabled by default and gated by
  `ENABLE_EXTERNAL_NETWORK`.
- Frontend lint uses `eslint .` because `next lint` is not valid for the
  installed Next.js version.
- Axios was removed in favor of native `fetch`.
- Docker Compose, GitHub Actions, ignore rules, and environment templates were
  rewritten into valid maintainable files.

See [AUDIT_REPORT.md](AUDIT_REPORT.md) for command results and remaining risks.
