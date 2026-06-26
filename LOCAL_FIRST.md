# Local-First Privacy Notes

Annapurna-AI is a privacy-aware reference implementation for local meal planning.
By default, the app stores data in local SQLite and talks only to a local LLM
endpoint such as Ollama on `localhost:11434`.

## Local by default

- Meal plans are saved in a local SQLite database.
- Family profile labels, pantry inventory, Telugu/Andhra constraints, and
  grocery optimization context are saved locally with the generated plan.
- The default LLM provider is Ollama.
- USDA and PubMed fetchers are disabled.
- `ENABLE_EXTERNAL_NETWORK=false` blocks optional fetchers even if their feature
  flags are accidentally enabled.
- `ENABLE_EXTERNAL_NETWORK=false` also blocks non-local LLM endpoints.
- The frontend calls the backend through the local Next.js rewrite at
  `/api/python`.

## Optional external behavior

The following settings must be changed intentionally before external lookups run:

- `ENABLE_EXTERNAL_NETWORK=true`
- `ENABLE_USDA=true` plus `USDA_API_KEY`
- `ENABLE_PUBMED=true` plus `PUBMED_EMAIL`

When enabled, USDA queries go to FoodData Central and PubMed queries go to NCBI
E-utilities. User-entered dietary text may become part of those queries, so keep
external fetchers off for private use.

## Model switching boundary

Local model mode is the default and uses endpoints such as Ollama on
`localhost:11434`, LM Studio on localhost, llama.cpp on localhost, or
`host.docker.internal` for Docker-to-host local model access.

Cloud or external model mode requires both a non-local `LLM_BASE_URL` and
`ENABLE_EXTERNAL_NETWORK=true`. In that mode, prompt data can include family
role labels, pantry items, allergies, and dietary preferences, so use it only
when that data sharing is acceptable.

## Family profile privacy model

Annapurna uses data minimization for personalization:

- Role labels instead of real names.
- Age groups instead of exact ages.
- Appetite bands instead of weights or calorie targets.
- Cooking tags instead of medical history.
- Local SQLite storage by default.

## No telemetry claim

The application code does not include analytics, Sentry, PostHog, LangSmith, or
other telemetry hooks. LiteLLM callbacks are disabled in the backend service.
Dependency packages may contain optional integrations, so review new dependencies
before adding them.

## Wellness boundary

Annapurna-AI provides general wellness meal-planning ideas only. It is not a
medical device, clinical nutrition system, or compliance product. It does not
claim HIPAA, GDPR, medical, or clinical compliance.
