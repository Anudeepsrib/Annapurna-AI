# Local-First Privacy Notes

Annapurna-AI is a privacy-aware reference implementation for local meal planning.
By default, the app stores data in local SQLite and talks only to a local LLM
endpoint such as Ollama on `localhost:11434`.

## Local by default

- Meal plans are saved in a local SQLite database.
- The default LLM provider is Ollama.
- USDA and PubMed fetchers are disabled.
- `ENABLE_EXTERNAL_NETWORK=false` blocks optional fetchers even if their feature
  flags are accidentally enabled.
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

## No telemetry claim

The application code does not include analytics, Sentry, PostHog, LangSmith, or
other telemetry hooks. LiteLLM callbacks are disabled in the backend service.
Dependency packages may contain optional integrations, so review new dependencies
before adding them.

## Wellness boundary

Annapurna-AI provides general wellness meal-planning ideas only. It is not a
medical device, clinical nutrition system, or compliance product. It does not
claim HIPAA, GDPR, medical, or clinical compliance.
