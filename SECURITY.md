# Security Policy

## Secrets and local data

Do not commit `.env`, `.env.*`, local SQLite databases, generated plans, logs,
caches, or model artifacts. The repository keeps only `env.example` as a safe
template.

Local meal plans may include sensitive dietary preferences. Treat
`annapurna.db`, exported plans, generated grocery lists, and logs as private
user data.

## Optional external APIs

USDA and PubMed integrations are disabled by default. Enable them only when you
understand that search text can leave your machine. Do not place real API keys in
source control.

## Vulnerability reporting

Open a private security advisory on GitHub if available, or contact the project
maintainer with a concise report including affected files, reproduction steps,
and expected impact.

## Local scanning

Recommended checks before publishing changes:

```bash
python -m compileall backend/app
cd backend && ruff check . && pytest
npm run lint
npm run build
npm audit --audit-level=high
gitleaks detect --source .
```

If `gitleaks` is unavailable, use `detect-secrets scan --all-files` as a
secondary check and manually review the output.
