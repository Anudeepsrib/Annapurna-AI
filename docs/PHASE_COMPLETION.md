# V2 Phase Completion

All 30 phases in the V2 production-hardening brief are implemented. The
milestone reports retain their historical verification results; this document
maps the final repository state to the broader phase checklist.

Current verification snapshot (2026-09-20): 78 backend tests, three offline
planning scenarios, Ruff, frontend ESLint, TypeScript, Next.js production build,
dependency audits, migration checks, and tracked-file secret scanning pass.

| Phase | Completed behavior |
| --- | --- |
| 1 | `PlanService` coordinates extracted constraints, candidates, validation, scoring, fallback, grocery compilation, and repositories. |
| 2 | Versioned local ontology contains 138 Telugu/South-Indian household ingredients. |
| 3 | Deterministic exact, alias, token, conservative fuzzy, ambiguous, and unresolved matching. |
| 4 | Decimal weight, volume, and count units with same-dimension conversion only. |
| 5 | Structured pantry is authoritative while legacy text and `PlanRequest` remain compatible. |
| 6 | Purchase, consume, adjust, expire, discard, and restock events with optimistic versions. |
| 7 | Typed hard constraints run independently of the LLM. |
| 8 | Typed soft preferences remain scoring inputs rather than validity rules. |
| 9 | Configurable heuristic scoring covers pantry, expiry, preferences, feedback, variety, reuse, repetition, missing items, and waste. |
| 10 | Candidate generation → validation → ranking → pantry/grocery → persistence, with deterministic fallback. |
| 11 | Grocery compiler merges identities, structured requirements, pantry quantities, minimum stock, and manual items without inventing missing quantities. |
| 12 | Grocery items carry category and advisory Indian/bulk/general store affinity; an optional retailer protocol isolates future adapters. |
| 13 | `/today` provides meals, preparation, missing items, expiry, leftovers, and execution actions. |
| 14 | One meal is replaced and validated without regenerating the week; groceries recalculate. |
| 15 | Locks survive single-meal, day, and full preference/household regeneration; conflicts require unlocking. |
| 16 | Leftovers have editable servings/use-by state, can be consumed, and can be referenced by a planned slot. |
| 17 | Execution and all six feedback signals persist; documented title weights influence later candidate ranking. |
| 18 | A validated 10-recipe local catalog separates recipe metadata and quantified ingredients from meal text. |
| 19 | Planner prompts and generation component versions are explicit and persisted. |
| 20 | Every generation records provenance without chain-of-thought. |
| 21 | Durable idempotency replays matching requests and rejects conflicting reuse. |
| 22 | Alembic owns four backwards-compatible SQLite migrations. |
| 23 | Domain-specific plan, pantry, and feedback repositories isolate persistence behavior. |
| 24 | Stable validation, constraint, LLM, pantry, grocery, idempotency, command, not-found, and internal error codes share one envelope. |
| 25 | Validated request IDs flow through frontend requests and structured context logs without prompt/profile logging. |
| 26 | Configurable timeout, bounded retry/backoff, process-local circuit breaker, and deterministic fallback. |
| 27 | Profile UI is decomposed and backend parsing remains authoritative. |
| 28 | Primary navigation is Today, Week, Pantry, Shop, and Family. |
| 29 | Lightweight commands compile into typed, validated actions before state mutation. |
| 30 | Existing general-wellness guardrails and evidence boundaries remain enforced. |

## Required edge cases

The automated suite covers all 20 required cases: meat in vegetarian plans,
egg-free conflicts, festival onion/garlic rules, ingredient aliases, 2 kg ↔
2000 g conversion, expired and insufficient pantry stock, repetition, child
spice preference, replacement grocery recalculation, household-size changes,
eating out, leftovers, unavailable/timeout/malformed LLM behavior, unknown
ingredients, stale pantry updates, duplicate generation, and lock survival.

## Deliberate product boundaries

- Retailer adapters are interfaces only; there is no checkout or required cloud
  dependency.
- The recipe catalog is intentionally small and curated rather than scraped.
- Feedback is a visible heuristic, not black-box machine learning.
- Commands are intentionally limited to validated household actions instead of
  becoming a general chatbot.

## Current Documentation

- [User Guide](USER_GUIDE.md) covers the finished household workflows.
- [Architecture](../ARCHITECTURE.md) and [Repository Structure](REPOSITORY_STRUCTURE.md)
  describe the current source boundaries after the API and grocery-domain
  reorganization.
- [Backend Guide](../backend/README.md) lists current routes and verification
  commands.
- Milestone reports remain dated historical records; their intermediate test
  counts and “next milestone” notes are not the current completion status.
