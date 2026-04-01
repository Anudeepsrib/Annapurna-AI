# Annapurna-AI — Local Setup Guide (5 Minutes)

**"Clone it. Run it. Own it. Your food data never leaves your machine."**

## Prerequisites

- Git
- Node.js 20+
- Python 3.11+
- Ollama (or any local LLM server like LM Studio, llama.cpp)

## Step 1: Install a Local LLM (Ollama Recommended)

### macOS/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Download from [https://ollama.com](https://ollama.com)

### Pull a Model
```bash
ollama pull llama3.2:latest
```

Ollama auto-serves at `http://localhost:11434`

## Step 2: Clone & Configure

```bash
git clone https://github.com/Anudeepsrib/Annapurna-AI.git
cd Annapurna-AI

# Copy environment template
cp env.example backend/.env
```

Edit `backend/.env` only if you're NOT using Ollama defaults.

## Step 3: Install Dependencies

### Frontend
```bash
npm install
```

### Backend
```bash
cd backend
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
cd ..
```

## Step 4: Run

### Terminal 1 — Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Terminal 2 — Frontend
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Alternative: Docker
```bash
docker compose up --build
```
Open [http://localhost:3000](http://localhost:3000)

## Your Data

- **Location:** `backend/annapurna.db` (SQLite file)
- **Backup:** Simply copy the `.db` file
- **Reset:** Delete the `.db` file and restart

## Configuration Options

### Using LM Studio Instead of Ollama

1. Download [LM Studio](https://lmstudio.ai)
2. Load a model and start the local server (runs on `http://localhost:1234`)
3. Edit `backend/.env`:
   ```
   LLM_PROVIDER=lmstudio
   LLM_BASE_URL=http://localhost:1234/v1
   LLM_MODEL=your-model-name
   ```

### Using llama.cpp

```bash
# Start llama.cpp server
./llama-server -m model.gguf --port 8080
```

Edit `backend/.env`:
```
LLM_PROVIDER=llamacpp
LLM_BASE_URL=http://localhost:8080/v1
LLM_MODEL=your-model-name
```

### Enable External APIs (Optional)

To enrich meal plans with USDA nutrition data or PubMed evidence:

1. Get a USDA API key: https://fdc.nal.usda.gov/api-key-signup.html
2. Edit `backend/.env`:
   ```
   ENABLE_USDA=true
   USDA_API_KEY=your-key-here
   ENABLE_PUBMED=true
   ```

## Privacy Guarantees

- ✅ **No telemetry** - No analytics or tracking
- ✅ **No outbound calls by default** - USDA/PubMed are opt-in, disabled by default
- ✅ **LLM calls stay on localhost** - Default endpoint is `localhost`
- ✅ **Database is a file** - You control your data
- ✅ **No accounts** - No passwords, no sessions, no cloud auth

## Model Recommendations

| Model | Size | Quality | Speed |
|-------|------|---------|-------|
| Llama 3.2 3B | ~2GB | Good | Fast |
| Llama 3.2 7B | ~4GB | Very Good | Moderate |
| Mistral 7B | ~4GB | Very Good | Moderate |
| Phi-3 Mini | ~2GB | Good | Very Fast |

For best results, use a 7B+ parameter model. 3B models work but may produce less varied meal plans.

## Troubleshooting

### "Connection failed" when testing LLM
- Is Ollama running? Check with `ollama list`
- Is the port correct? Default is 11434
- Try: `curl http://localhost:11434/api/tags`

### Frontend can't connect to backend
- Is the backend running on port 8000?
- Check `next.config.ts` has the correct rewrite rule

### Missing dependencies
```bash
# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

## Architecture

```
Your Computer
├── Frontend: Next.js (localhost:3000)
├── Backend: FastAPI (localhost:8000)
├── Database: SQLite (annapurna.db)
└── LLM: Ollama (localhost:11434)
```

Zero data leaves your machine.
