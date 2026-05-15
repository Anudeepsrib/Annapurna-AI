from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


class Settings(BaseSettings):
    """Application settings with local-first, privacy-preserving defaults."""

    PROJECT_NAME: str = "Annapurna-AI Local"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    APP_ENV: Literal["development", "test", "production"] = "development"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: LOCAL_CORS_ORIGINS.copy())

    DATABASE_URL: str = "sqlite+aiosqlite:///./annapurna.db"

    # Local LLM defaults. API keys are optional and disabled by default.
    LLM_PROVIDER: Literal["ollama", "lmstudio", "llamacpp", "custom"] = "ollama"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.2:latest"
    LLM_API_KEY: str | None = None

    # External fetchers are opt-in and gated behind ENABLE_EXTERNAL_NETWORK.
    ENABLE_EXTERNAL_NETWORK: bool = False
    ENABLE_USDA: bool = False
    USDA_API_KEY: str | None = None
    ENABLE_PUBMED: bool = False
    PUBMED_EMAIL: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("["):
                # Let pydantic surface JSON errors clearly if malformed.
                import json

                parsed = json.loads(value)
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS JSON must be a list")
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("LLM_API_KEY", "USDA_API_KEY", "PUBMED_EMAIL", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def validate_privacy_and_production(self) -> "Settings":
        if self.ENABLE_USDA and not self.USDA_API_KEY:
            raise ValueError("USDA_API_KEY is required when ENABLE_USDA=true")
        if self.ENABLE_PUBMED and not self.PUBMED_EMAIL:
            raise ValueError("PUBMED_EMAIL is required when ENABLE_PUBMED=true")
        if (self.ENABLE_USDA or self.ENABLE_PUBMED) and not self.ENABLE_EXTERNAL_NETWORK:
            raise ValueError(
                "ENABLE_EXTERNAL_NETWORK must be true before USDA or PubMed fetchers can be enabled"
            )
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be false when APP_ENV=production")
            if "CORS_ORIGINS" not in self.model_fields_set:
                raise ValueError("CORS_ORIGINS must be explicitly set in production")
            if not self.CORS_ORIGINS or "*" in self.CORS_ORIGINS:
                raise ValueError("Production CORS_ORIGINS must be explicit and cannot include '*'")
        return self


settings = Settings()
