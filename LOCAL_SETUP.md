# Local Setup

This guide installs and starts Annapurna-AI with local-first defaults. After the
app is running, continue with the [User Guide](docs/USER_GUIDE.md).

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer with npm
- Ollama
- Git

Install Ollama from [ollama.com](https://ollama.com), make sure its local service
is running, and download the default model:

```bash
ollama pull llama3.2:latest
```

## Automated Setup

From the repository root, run the script for your platform:

```powershell
.\scripts\setup.ps1
```

```bash
bash scripts/setup.sh
```

The scripts create `backend/venv`, install backend and frontend dependencies,
copy `env.example` to `backend/.env` when needed, apply Alembic migrations, and
pull the default Ollama model.

## Manual Setup

Clone the repository:

```bash
git clone https://github.com/Anudeepsrib/Annapurna-AI.git
cd Annapurna-AI
```

Backend on Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item ..\env.example .env
python -m alembic upgrade head
```

Backend on macOS or Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp ../env.example .env
python -m alembic upgrade head
```

Install the frontend from the repository root:

```bash
npm install
```

## Start the Application

Start the backend from `backend` with its virtual environment activated:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In a second terminal at the repository root, start Next.js:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Verify the Installation

1. Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) and confirm
   the response contains `"status": "ok"`.
2. Open **Settings** in the app and choose **Test Connection**.
3. If the model is missing, run `ollama list` and then
   `ollama pull llama3.2:latest`.
4. Open **Family**, keep the sample values, and generate a plan.

The backend API schema is available at
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Docker Alternative

To run the backend container against Ollama on the host:

```bash
docker compose up --build backend
```

To run both the backend and the optional Ollama container:

```bash
docker compose --profile ollama up --build
docker compose --profile ollama exec ollama ollama pull llama3.2:latest
```

Docker binds services to localhost and stores the SQLite database in the
`annapurna-data` named volume. The frontend still runs separately with
`npm run dev`.

## Configuration

Backend configuration belongs in `backend/.env`. Frontend-only overrides belong
in `.env.local`. Never put secrets in a `NEXT_PUBLIC_*` variable.

The defaults keep Ollama, SQLite, and all optional fetchers local/offline. See
the [README configuration section](README.md#configuration) and [Local-First
Privacy Notes](LOCAL_FIRST.md) before enabling external access.

## Updating an Existing Checkout

After pulling changes:

```bash
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
cd ..
npm install
```

Back up `backend/annapurna.db` before migrations if it contains household data
you cannot recreate.
