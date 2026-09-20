# Fix Log

This is the condensed hardening record for Annapurna-AI. Historical command
output remains in [AUDIT_REPORT.md](AUDIT_REPORT.md); the final Phase 1–30 map is
in [docs/PHASE_COMPLETION.md](docs/PHASE_COMPLETION.md).

## Runtime and Privacy

- Centralized validated settings and local-only defaults.
- Added explicit external-network gates for non-local models, USDA, and PubMed.
- Removed browser font/network dependencies and centralized frontend requests
  on native `fetch`.
- Added privacy-safe request IDs and structured logs that omit prompts,
  household profiles, pantry contents, secrets, and query strings.

## Planning and Household Workflows

- Added typed constraints/preferences, schema and hard-rule validation,
  deterministic fallback, candidate ranking, and generation provenance.
- Added canonical ingredient/unit handling, structured pantry inventory and
  transactions, quantified recipes, pantry subtraction, minimum stock, manual
  shopping items, and use-soon grouping.
- Added Today, execution status, feedback, leftovers, locks, one-meal
  replacement, day regeneration, and validated household commands.
- Added durable request idempotency and bounded LLM timeout/retry/circuit
  behavior.

## Engineering and Documentation

- Added four Alembic migrations, repositories, offline evaluations, CI quality
  and security gates, Docker Compose, and safe environment templates.
- Grouped API handlers by capability and moved grocery compilation into the
  grocery domain.
- Added the [User Guide](docs/USER_GUIDE.md), [documentation
  index](docs/README.md), current architecture, setup, privacy, security, and
  contributor placement guides.

Current verification: 78 backend tests and three offline evaluation scenarios
pass, with Ruff, frontend ESLint, TypeScript, Next.js build, dependency audits,
migration checks, and tracked-file secret scanning clean as of 2026-09-20.
