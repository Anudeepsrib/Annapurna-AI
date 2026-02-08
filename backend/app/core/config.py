from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Annapurna-AI Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # --- Security & Auth ---
    # Secret Key for JWT (Generate with: openssl rand -hex 32)
    SECRET_KEY: str = "change_this_to_a_secure_random_string_in_production" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    
    # CORS (Allow all for development, restrict in production)
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # --- Database ---
    # Async Postgres URL (e.g., postgresql+asyncpg://user:pass@host:port/db)
    # Defaulting to None so build passes without it. 
    # Must be set in production environment variables.
    DATABASE_URL: Optional[str] = None
    
    # --- External Services ---
    OPENAI_API_KEY: Optional[str] = None
    USDA_API_KEY: Optional[str] = None
    
    # --- Observability ---
    LITELLM_CALLBACK: Optional[str] = None
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    HELICONE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Ignore extra env vars
    )

settings = Settings()
