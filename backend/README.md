# Annapurna-AI Backend

FastAPI backend for local-first meal planning.

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Windows activation:

```powershell
.\venv\Scripts\Activate.ps1
```

## Endpoints

- `GET /health`
- `GET /api/v1/health`
- `POST /api/v1/generate-plan`
- `GET /api/v1/plan`
- `GET /api/v1/grocery-list`
- `GET /api/v1/evidence/{topic}`
- `GET /api/v1/mcp/ifct/search?query=rice`
- `GET /api/v1/mcp/usda/search?query=rice`

## Privacy Defaults

- SQLite is local.
- Ollama is the default LLM provider.
- USDA and PubMed are disabled by default.
- `ENABLE_EXTERNAL_NETWORK=false` blocks optional fetchers.
- Health endpoints do not return API keys, database paths, or stack traces.

## Safety

This backend provides general wellness planning only. It validates LLM output
before saving and applies guardrails for medical-condition, pregnancy, kidney
disease, severe allergy, pediatric, medication-interaction, eating-disorder, and
extreme weight-loss prompts.
