# Milestone 9: Production Resilience and Evaluation Gates

> Historical implementation record. This milestone and the full V2 phase map
> are complete. See [Phase Completion](PHASE_COMPLETION.md) for current status
> and verification.

## Baseline

- Milestone 8 backend suite: 66 passed.
- Backend Ruff, frontend ESLint, TypeScript, and production build: passed.

## Files changed

- API request correlation, stable error taxonomy, validation envelope, and
  privacy-safe structured logging.
- Configurable LLM timeout/retry/circuit-breaker behavior.
- Generation idempotency model, repository methods, API header support, and
  Alembic migration `0004_idempotency`.
- Frontend request IDs and generation idempotency keys.
- Next.js and its ESLint preset upgraded to the patched 16.3.5 release after
  the dependency audit identified advisories in 16.2.6.
- Offline planner scenarios, runner, CI evaluation gate, and CI secret scan.
- Resilience regression tests and operator documentation.

## Architecture changes

- Every request receives a validated or generated `X-Request-ID`, which is
  returned to the client and bound to structured logs.
- API failures use stable machine-readable codes and include the request ID.
- LLM failures are bounded by timeout and retry settings; consecutive failures
  open a short, in-process circuit and preserve deterministic fallback.
- Idempotency records persist the request hash and exact result in local SQLite.
  Matching retries replay without another model call or plan write.
- Network-free evaluation scenarios validate invariant behavior independently
  of unit tests and exact generated wording.

## Behavior changes

- `POST /api/v1/generate-plan` accepts `Idempotency-Key`.
- Reusing the key with identical input returns the original generation metadata;
  different input returns HTTP 409 with `IDEMPOTENCY_CONFLICT`.
- Validation and domain errors share an `{error: {message, code, request_id}}`
  envelope.
- Request logs avoid prompts, dietary text, pantry contents, secrets, and query
  strings.

## Tests added

- Success/error request-ID propagation and stable validation errors.
- Idempotent replay, single model invocation, and conflicting-key rejection.
- Bounded model retries and circuit opening.
- Three offline scenarios covering festival restrictions, dairy allergy, and
  pantry-aware vegetarian planning.

## Tests run

- `py -m pytest -q`: 70 passed.
- `py -m evals.run_evals`: 3 scenarios passed.
- `py -m ruff check .`: passed.
- `py -m pip_audit -r requirements.txt`: no known vulnerabilities.
- Repository-local ESLint: passed.
- `tsc --noEmit`: passed.
- Next.js production build: passed.
- `npm audit --audit-level=high`: 0 vulnerabilities.

## Remaining risks

- The circuit breaker is process-local; multi-process deployments do not share
  failure state. This matches the current single-machine deployment target.
- Generation idempotency is durable but optimized for one local writer. A
  future multi-writer deployment should make plan/result persistence a single
  serializable transaction.
- Offline evaluations cover deterministic invariants, not subjective meal
  quality or live-model drift.

## Completion

Milestones 1–9 are implemented. Future work is product expansion rather than a
required milestone in the current roadmap.
