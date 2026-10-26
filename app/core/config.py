"""Application configuration.

All settings are read from the environment (and an optional `.env` file) via
pydantic-settings, so there is a single, typed, validated source of truth. Nothing
elsewhere in the codebase reads ``os.environ`` directly.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = two levels up from this file (app/core/config.py -> project root).
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Typed application settings with local-first defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = Field(default="AI Product Intelligence Platform", alias="APP_NAME")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    # Comma-separated browser origins allowed to call the API (the Next.js dev
    # server runs on :3000). Use "*" to allow any origin.
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000", alias="CORS_ORIGINS"
    )
    # Per-IP requests/minute across the whole API. 0 disables it (tests do this).
    # Exists to stop a runaway script from running up real Anthropic costs against
    # the publicly reachable, unauthenticated analyze and chat endpoints.
    rate_limit_per_minute: int = Field(default=30, alias="RATE_LIMIT_PER_MINUTE")

    # --- Anthropic ---
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    # Authoritative model id — do not append a date suffix.
    anthropic_model: str = Field(default="claude-opus-4-8", alias="ANTHROPIC_MODEL")
    analysis_concurrency: int = Field(default=5, alias="ANALYSIS_CONCURRENCY")

    # --- Database ---
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/app.db", alias="DATABASE_URL"
    )

    # --- Vector store (Qdrant) ---
    # Either a local path (no server) OR a server URL. Path wins if both are set.
    qdrant_path: str | None = Field(default="./data/qdrant", alias="QDRANT_PATH")
    qdrant_url: str | None = Field(default=None, alias="QDRANT_URL")
    qdrant_collection: str = Field(default="knowledge_base", alias="QDRANT_COLLECTION")

    # --- Embeddings ---
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )

    # --- Reddit (optional — only the reddit connector needs these) ---
    # Public unauthenticated access to reddit.com/*.json now returns 403, so this
    # connector needs a real (free) OAuth app: https://www.reddit.com/prefs/apps
    reddit_client_id: str | None = Field(default=None, alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str | None = Field(default=None, alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(
        default="ai-product-intelligence-platform/0.1", alias="REDDIT_USER_AGENT"
    )

    @property
    def has_reddit_credentials(self) -> bool:
        return bool(
            self.reddit_client_id
            and self.reddit_client_id.strip()
            and self.reddit_client_secret
            and self.reddit_client_secret.strip()
        )

    @property
    def cors_origin_list(self) -> list[str]:
        """Parsed CORS origins. ``["*"]`` means allow any origin."""
        raw = (self.cors_origins or "").strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def has_anthropic_key(self) -> bool:
        """Whether AI-powered features (analysis, chat) are available."""
        return bool(self.anthropic_api_key and self.anthropic_api_key.strip())

    @property
    def qdrant_local_path(self) -> str | None:
        """Resolved local Qdrant path, or ``None`` when a server URL is configured."""
        if self.qdrant_url and self.qdrant_url.strip():
            return None
        return self.qdrant_path or "./data/qdrant"


@lru_cache
def get_settings() -> Settings:
    """Return a cached, process-wide :class:`Settings` instance."""
    return Settings()
