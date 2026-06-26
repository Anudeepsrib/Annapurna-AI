# Architecture

Annapurna-AI is a local-first meal-planning app. The default runtime has no
cloud authentication and no external data fetchers.

```mermaid
graph TB
    User["Browser"] --> Frontend["Next.js App Router"]
    Frontend --> Rewrite["/api/python rewrite"]
    Rewrite --> API["FastAPI /api/v1"]
    API --> PlanService["Plan Service"]
    API --> EvidenceService["Evidence Service"]
    API --> Settings["Settings API"]
    PlanService --> PrivacyModel["Family profile privacy model"]
    PlanService --> Pantry["Pantry inventory optimizer"]
    PlanService --> Rules["Telugu/Andhra rule validation"]
    PlanService --> SQLite[("Local SQLite")]
    PlanService --> LLM["LiteLLM -> local Ollama by default"]
    LLM -. explicit opt-in .-> CloudLLM["External OpenAI-compatible model"]
    EvidenceService --> LocalEvidence["Curated local evidence JSON"]
    EvidenceService -. opt-in .-> USDA["USDA FoodData Central"]
    EvidenceService -. opt-in .-> PubMed["PubMed E-utilities"]
```

## Components

- Frontend: Next.js 16, React 19, Tailwind CSS v4, Radix UI, TanStack Query.
- Backend: FastAPI, SQLModel, SQLite, LiteLLM, structlog.
- Local LLM: Ollama by default at `localhost:11434`.
- Family profile model: role labels, age groups, appetite bands, dietary tags,
  and privacy scope; avoids legal names and medical details.
- Pantry optimizer: uses provided pantry inventory to split grocery output into
  pantry-first, buy/replenish, and use-soon sections.
- Rule validator: rejects generated plans that violate active Telugu/Andhra
  dietary constraints such as no egg or festival no onion/garlic.
- Optional fetchers: USDA and PubMed, disabled unless
  `ENABLE_EXTERNAL_NETWORK=true` plus the specific fetcher settings.
- Optional external LLM endpoint: disabled unless `ENABLE_EXTERNAL_NETWORK=true`
  when `LLM_BASE_URL` is non-local.

## Safety Boundaries

The backend validates generated meal-plan JSON before saving it. Medical,
pregnancy, kidney disease, severe allergy, pediatric diet, epilepsy medication,
eating disorder, and extreme weight-loss prompts trigger general wellness
guardrails instead of disease-specific plans.
