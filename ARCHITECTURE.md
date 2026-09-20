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
    PlanService --> CandidatePlanner["Candidate Planner"]
    CandidatePlanner --> PromptV1["Versioned planner prompt"]
    CandidatePlanner --> LLM["LiteLLM -> local Ollama by default"]
    PlanService --> FallbackPlanner["Deterministic Fallback Planner"]
    PlanService --> GroceryCompiler["Grocery Compiler"]
    PlanService --> ConstraintEngine["Constraint Engine"]
    PlanService --> PlanValidator["Plan Validator"]
    PlanService --> PlanScorer["Plan Scorer"]
    PlanService --> PlanRepository["Plan Repository"]
    PlanService --> Ingredients["Ingredient ontology + normalizer"]
    PlanService --> PantryService["Structured pantry service"]
    PantryService --> PantryRepository["Pantry repository"]
    API --> TodayService["Today + Feedback Service"]
    TodayService --> FeedbackRepository["Feedback Repository"]
    PlanRepository --> SQLite[("Local SQLite + Alembic")]
    PantryRepository --> SQLite
    FeedbackRepository --> SQLite
    LLM -. explicit opt-in .-> CloudLLM["External OpenAI-compatible model"]
    EvidenceService --> LocalEvidence["Curated local evidence JSON"]
    EvidenceService -. opt-in .-> USDA["USDA FoodData Central"]
    EvidenceService -. opt-in .-> PubMed["PubMed E-utilities"]
```

## Components

- Frontend: Next.js 16, React 19, Tailwind CSS v4, Radix UI, TanStack Query.
- Frontend household surfaces: `/plan` for the week, `/pantry` for structured
  local inventory, `/list` for explainable shopping deductions, and `/profile`
  for family planning inputs. Profile sections are isolated UI components;
  parsing remains authoritative on the backend.
- Backend: FastAPI, SQLModel, SQLite, LiteLLM, structlog.
- Local LLM: Ollama by default at `localhost:11434`.
- Family profile model: role labels, age groups, appetite bands, dietary tags,
  and privacy scope; avoids legal names and medical details.
- Pantry optimizer: uses provided pantry inventory to split grocery output into
  pantry-first, buy/replenish, and use-soon sections.
- Constraint engine: compiles legacy Telugu/Andhra flags and dietary text into
  typed hard constraints and soft planning preferences.
- Plan validator: rejects schema-invalid plans and hard-constraint violations
  such as meat, egg, allergens, onion, or garlic before persistence.
- Plan scorer: ranks valid candidates using configurable heuristic weights for
  pantry and expiry use, preference match, variety, reuse, repetition, and
  waste. Scores are internal ranking signals, not user-facing claims.
- Candidate planner: turns versioned LLM output into one or more candidate
  payloads without deciding whether they are safe or valid.
- Deterministic fallback planner: owns the local seven-day fallback catalog and
  constraint-aware ingredient filtering.
- Grocery compiler: owns canonical ingredient merging, current-pantry matching,
  use-soon grouping, and unresolved quantity messaging.
- Plan service: coordinates pantry context, rules, candidate generation,
  validation, ranking, grocery compilation, and persistence.
- Optional fetchers: USDA and PubMed, disabled unless
  `ENABLE_EXTERNAL_NETWORK=true` plus the specific fetcher settings.
- Optional external LLM endpoint: disabled unless `ENABLE_EXTERNAL_NETWORK=true`
  when `LLM_BASE_URL` is non-local.
- Plan repository: owns plan persistence and latest-plan lookup without exposing
  SQLite behavior to the planning service.
- Generation provenance: every newly saved plan records a generation ID,
  timestamp, provider/model, prompt/planner/validator versions, source status,
  and whether deterministic fallback was used. Existing API routes remain valid.
- Ingredient domain: a versioned local JSON ontology plus deterministic name
  and unit normalization. Grocery/pantry identity matching uses canonical IDs;
  unresolved or ambiguous names are preserved rather than guessed.
- Pantry domain: structured inventory and append-only transaction events are
  persisted behind a domain-specific repository. Optimistic item versions
  prevent stale concurrent updates, and legacy free text is parsed only by the
  backend before planning.
- Household activity domain: meal execution status, transparent feedback
  signals, and lightweight leftovers persist locally behind a focused
  repository. `/today` combines these records with the latest plan, current
  pantry expiry, and missing-ingredient deductions.

## Database Migrations

Alembic owns schema changes. Run `cd backend && alembic upgrade head` before
starting the API after an update. The migrations preserve legacy plan JSON and
add structured pantry, meal execution, feedback, and leftover records. Runtime
startup no longer mutates the schema with `create_all`.

## Safety Boundaries

The backend validates generated meal-plan JSON before saving it. Medical,
pregnancy, kidney disease, severe allergy, pediatric diet, epilepsy medication,
eating disorder, and extreme weight-loss prompts trigger general wellness
guardrails instead of disease-specific plans.
