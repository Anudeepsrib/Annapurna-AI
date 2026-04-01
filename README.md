# Annapurna-AI 🍚

**"Clone it. Run it. Own it. Your food data never leaves your machine."**

**Annapurna-AI** is a **fully local, privacy-first AI meal planner** for South Indian vegetarian cooking.

The MVP focuses on **Andhra Telugu home cooking**, generating:

* a **weekly meal plan** that feels like real home food, and
* an **optimized grocery list** that minimizes waste and respects cultural cooking patterns,

while keeping **all your data on your computer** — zero cloud dependencies, zero data leaks.

---

## 🔒 Privacy First

- **No cloud authentication** — No accounts, passwords, or sign-ups
- **Local LLM processing** — Your meal data never leaves your machine
- **SQLite database** — Your data lives in a file you control (`annapurna.db`)
- **Optional online features** — USDA/PubMed integrations are opt-in, disabled by default
- **Zero telemetry** — No analytics, tracking, or data collection

---

## MVP Scope

* **Home cuisine:** South Indian vegetarian – Andhra Telugu household
* **Purpose:** General wellness and meal planning
* **Not supported:** Medical advice, disease-specific diets, supplements, weight-loss claims

This repository is a **local-first desktop application** optimized for privacy, simplicity, and end-to-end ownership.

---

## Core Features

* Weekly meal plan (breakfast / lunch / dinner)
* Staple-first planning (rice, dals, vegetables)
* Cultural meal structure enforcement
* Optimized grocery list with ingredient reuse
* Pantry-aware subtraction (optional)
* Culture-preserving substitutions
* Evidence-backed explanations with citations
* **Local LLM support** — Ollama (default), LM Studio, llama.cpp, or any OpenAI-compatible endpoint

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

## Tech Stack (Local-First)

### Frontend

* **Next.js** (App Router)
* **TypeScript**
* **Tailwind CSS** + **Radix UI**
* **TanStack Query**

### Backend

* **FastAPI** (Python 3.11+)
* **SQLModel** (SQLite for local persistence)
* **LiteLLM** (Unified LLM Interface)
* **aiosqlite** (Async SQLite driver)
* **Structlog** (Structured JSON Logging)

### AI (Local)

* **Ollama** (default — runs locally on your machine)
* Supports: Llama 3.2, Mistral, Phi-3, or any GGUF model
* Also compatible with: LM Studio, llama.cpp, LocalAI

### Deployment

* **Local development**: `npm run dev` + `uvicorn app.main:app --reload`
* **Docker**: `docker compose up --build`
* **Your data**: Stored in `backend/annapurna.db` (SQLite file)

---

## Quick Start (5 Minutes)

### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:** Download from [ollama.com](https://ollama.com)

### 2. Pull a Model

```bash
ollama pull llama3.2:latest
```

### 3. Clone & Setup

```bash
git clone https://github.com/Anudeepsrib/Annapurna-AI.git
cd Annapurna-AI

# Run setup script
# macOS/Linux:
bash scripts/setup.sh

# Windows PowerShell:
.\scripts\setup.ps1
```

### 4. Run

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Configuration

Create `backend/.env` (or copy from `env.example`):

```bash
# LLM Settings (defaults work with Ollama)
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:latest

# Database (SQLite — local file)
DATABASE_URL=sqlite+aiosqlite:///./annapurna.db

# Optional: Enable external APIs (requires internet)
ENABLE_USDA=false
ENABLE_PUBMED=false
USDA_API_KEY=  # Get from https://fdc.nal.usda.gov/api-key-signup.html
```

---

## Repository Structure

```
annapurna-ai/
├── app/                    # Next.js app
│   ├── settings/           # Local LLM configuration UI
│   ├── profile/            # Meal preferences
│   ├── plan/               # Generated meal plans
│   └── ...
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes
│   │   ├── core/           # Config, database
│   │   ├── services/       # LLM, planning, evidence
│   │   └── models/         # SQLModel schemas
│   ├── data/               # Seed recipes, nutrition data
│   └── annapurna.db        # Your local SQLite database
├── components/ui/          # Radix UI components
├── scripts/                # Setup scripts
└── LOCAL_SETUP.md          # Detailed setup guide
```

---

## Model Recommendations

| Model | Size | Quality | Best For |
|-------|------|---------|----------|
| Llama 3.2 3B | ~2GB | Good | Fast, structured output |
| Llama 3.2 7B | ~4GB | Very Good | Best balance quality/speed |
| Mistral 7B | ~4GB | Very Good | Creative meal variety |
| Phi-3 Mini | ~2GB | Good | Low resource usage |

For best results, use a 7B+ parameter model.

---

## How It Works

1. User sets preferences (household size, spice level)
2. Local LLM generates candidate meals
3. Cultural consistency rules validate authenticity
4. Weekly plan is optimized for ingredient reuse
5. Grocery list is consolidated
6. Evidence notes attached (from local database or optional APIs)

**All processing happens locally** — no data sent to external servers.

---

## Your Data

- **Location**: `backend/annapurna.db`
- **Format**: SQLite (standard, portable)
- **Backup**: Copy the `.db` file
- **Reset**: Delete the `.db` file and restart
- **Privacy**: You own and control everything

---

## Safety & Disclaimer

Annapurna-AI provides **general wellness and educational information only**.

It does **not** provide medical advice, diagnosis, or treatment.
Users with medical conditions should consult qualified professionals.

---

## Roadmap

* v0.1: Local-first Andhra Telugu planner ✅
* v0.2: Meal swaps + saved plans
* v0.3: More South Indian regional cuisines
* v0.4: Pantry integration + nutrition tracking

---

## Status

✅ **Local MVP Ready**

Zero cloud dependencies. Fully functional offline.
