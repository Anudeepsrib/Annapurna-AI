# Annapurna-AI 🍚

**Annapurna-AI** is an **India-first, culture-aware AI meal planner and grocery assistant**.

The MVP focuses on **South Indian vegetarian – Andhra Telugu home cooking**, generating:

* a **weekly meal plan** that feels like real home food, and
* an **optimized grocery list** that minimizes waste and respects cultural cooking patterns,

while providing **evidence-grounded explanations** for general wellness (not medical advice).

---

## MVP Scope (Strict)

* **Home cuisine:** South Indian vegetarian – Andhra Telugu household
* **Purpose:** General wellness and meal planning
* **Not supported:** Medical advice, disease-specific diets, supplements, weight-loss claims

This repository represents an **early MVP**, optimized for **low cost**, **clarity**, and **end-to-end delivery**.

---

## Core Features (MVP)

* Weekly meal plan (breakfast / lunch / dinner)
* Staple-first planning (rice, dals, vegetables)
* Cultural meal structure enforcement
* Optimized grocery list with ingredient reuse
* Pantry-aware subtraction (optional)
* Culture-preserving substitutions
* Evidence-backed explanations with citations
* Gemini-first LLM usage (pluggable for others later)

---

## Cultural Constraints (Non-Negotiable)

The planner **must**:

* Use rice-centric meals
* Prefer lentils (toor, moong, urad, chana) for protein
* Use groundnut or sesame oil
* Follow Andhra Telugu meal patterns
* Avoid paneer-centric, North Indian, or Western defaults

This is **home food**, not restaurant food.

---

## Tech Stack (MVP – Low Cost)

### Frontend

* **Next.js** (App Router)
* **TypeScript**
* Minimal UI (Tailwind optional)

### Backend

*   **FastAPI** (Python 3.11+)
*   **LiteLLM** (Unified LLM Interface + Observability)
*   **Structlog** (Structured JSON Logging)
*   Top-tier Observability (Langfuse/Helicone integration)

### AI

*   **Gemini** (Primary via LiteLLM)
*   Architecture supports instant switching to:
    *   OpenAI
    *   Anthropic
    *   xAI (Grok)
    *   Any custom model supported by LiteLLM

### Deployment

*   **Frontend**: Vercel (Next.js)
*   **Backend**: Render (FastAPI)
*   **Guide**: See [PRODUCTION_GUIDE.md](./PRODUCTION_GUIDE.md) for step-by-step production deployment.

---

## Repository Structure (Initial)

```
annapurna-ai/
  app/                 # Next.js app
  src/
    planner/            # meal planning + optimization logic
    culture/            # Andhra Telugu rules & validators
    grocery/            # grocery consolidation logic
    evidence/           # citation + explanation logic
    data/               # seed recipes, staples, references
  docs/
    scope.md
    safety.md
```

---

## How the MVP Works (High Level)

1. User profile is interpreted with **Andhra Telugu defaults**
2. Candidate meals are generated
3. Cultural consistency rules validate authenticity
4. Weekly plan is optimized for reuse and simplicity
5. Grocery list is consolidated and cleaned
6. Evidence notes are attached conservatively

No free-form hallucinated meal plans are allowed.

---

## Running Locally

### Frontend (Next.js)

```bash
git clone https://github.com/<your-username>/annapurna-ai.git
cd annapurna-ai
npm install
npm run dev
```

### Backend (FastAPI)

Open a new terminal:

```bash
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\uvicorn main:app --reload
```

Create `.env.local`:

```bash
GEMINI_API_KEY=your_api_key_here
```

---

## Safety & Disclaimer

Annapurna-AI provides **general wellness and educational information only**.

It does **not** provide medical advice, diagnosis, or treatment.
Users with medical conditions should consult qualified professionals.

---

## Roadmap (Short)

* v0.1: Andhra Telugu vegetarian weekly planner
* v0.2: Meal swaps + saved plans
* v0.3: Multi-LLM routing + more Andhra subregions
* v0.4: Expand to other Indian cuisines

---

## Status

🚧 **Active MVP build**
Expect breaking changes.
