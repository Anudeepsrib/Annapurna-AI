# Annapurna-AI Backend (Evidence System)

A deterministic, safety-first evidence backend for the Annapurna-AI meal planner.

## Architecture

1.  **Curated Evidence (`/data/evidence`)**:
    *   **Guidelines**: ICMR-NIN 2024 data.
    *   **Food Composition**: IFCT 2017 data.
    *   *Stored as versioned JSON files for auditability.*

2.  **MCP Tools (`/app/services`)**:
    *   `PubMedClient`: Fetches research abstracts if curated evidence is missing.
    *   `USDAClient`: Backup food data source.

3.  **Orchestrator**:
    *   Checks curated data first.
    *   Blocks unsafe/medical queries (e.g., "diabetes", "cure").
    *   Falls back to PubMed for general wellness research.

## Usage

### Run locally
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### API Endpoints

- **GET /api/v1/evidence/{topic}**: Smart evidence retrieval.
- **GET /api/v1/mcp/ifct/search?query=...**: Search Indian Food Tables.
- **GET /api/v1/mcp/usda/search?query=...**: Search USDA database.

## Safety Constraints

- **No Medical Advice**: Queries related to disease treatment are blocked.
- **Disclaimer**: All responses include a standard wellness disclaimer.
- **Audit Logging**: Every request is logged with timestamp and query details.
