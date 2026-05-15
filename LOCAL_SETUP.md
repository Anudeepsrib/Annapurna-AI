# Local Setup

Use the canonical setup instructions in [README.md](README.md#quick-start).

Short version:

```bash
ollama pull llama3.2:latest
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Windows PowerShell activation:

```powershell
.\venv\Scripts\Activate.ps1
```

Frontend:

```bash
npm install
npm run dev
```
