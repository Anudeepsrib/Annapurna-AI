from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Annapurna-AI Local"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # --- LLM Configuration (Local First) ---
    # Provider: ollama | lmstudio | llamacpp | custom
    LLM_PROVIDER: str = "ollama"
    # Base URL for LLM API
    LLM_BASE_URL: str = "http://localhost:11434"  # Ollama default
    # Model name
    LLM_MODEL: str = "llama3.2:latest"
    # API key (usually not needed for local, but for OpenAI-compatible endpoints)
    LLM_API_KEY: str = "not-needed"

    # --- Database ---
    # SQLite for local-first (file-based, user owns their data)
    DATABASE_URL: str = "sqlite+aiosqlite:///./annapurna.db"

    # --- Optional External APIs (disabled by default for privacy) ---
    # Enable USDA nutrition lookups (requires internet + API key)
    ENABLE_USDA: bool = False
    USDA_API_KEY: Optional[str] = None

    # Enable PubMed evidence search (requires internet)
    ENABLE_PUBMED: bool = False

    # --- Legacy/Compatibility (kept for config migration) ---
    # Old OpenAI key - not used in local mode but kept to avoid breaking
    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Ignore extra env vars
    )

settings = Settings()
