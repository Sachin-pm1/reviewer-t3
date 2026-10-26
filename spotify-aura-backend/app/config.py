"""Settings — the only place that reads environment variables.

Mirrors the parent repo's rule (app/core/config.py): every secret and every
env-driven knob is declared here and nowhere else, so there's exactly one
place to audit for what this service reads from its environment.
"""

from __future__ import annotations

import secrets
from functools import lru_cache

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-8"

    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    # Must exactly match a Redirect URI registered on the Spotify app (Dashboard
    # → Settings → Redirect URIs). 127.0.0.1 (not "localhost") is exempt from
    # Spotify's HTTPS requirement for loopback addresses, so plain http works
    # for local dev. Unless the app has extended quota, every Spotify account
    # that will sign in must also be added under Dashboard → User Management.
    spotify_redirect_uri: str = "http://127.0.0.1:8010/auth/spotify/callback"
    # Encrypts stored Spotify access/refresh tokens at rest (Fernet/AES128).
    # Empty means "generate a random one for this process" (fine for local dev,
    # same tradeoff as jwt_secret below) — but unlike a JWT, a token encrypted
    # under a since-rotated key can never be decrypted again, so a restart with
    # no fixed key silently forces every connected user to reconnect Spotify.
    # Set a real value before deploying (`python -c "from cryptography.fernet
    # import Fernet; print(Fernet.generate_key().decode())"`).
    token_encryption_key: str = ""

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    # Where to send the browser back to after the Spotify OAuth redirect
    # round trip completes (a full-page navigation, not a CORS-governed
    # fetch, so this is independent of cors_origins above).
    frontend_base_url: str = "http://127.0.0.1:3010"
    # A single browsing pass through this app easily fires 20-30 requests on
    # its own (Discovery alone fires 8 parallel /catalog/experience-track
    # calls on mount, Soundtrack 7, Commute 4, plus every Spotify-aware page
    # calling /me/spotify/overview) — 30/min was tuned only around the one
    # expensive public endpoint and punished ordinary navigation. Still a
    # real floor against a runaway/abusive script, just not this tight.
    rate_limit_per_minute: int = 120
    # Stricter, separate budget for /auth/signin + /auth/signup specifically —
    # bcrypt makes each guess expensive already, but credential-stuffing at
    # 30/min (the general limit, shared with every other route) is still a lot
    # of guesses over a day. Governed by the same rate_limit_per_minute<=0 "off
    # for tests" switch, just a tighter number when rate limiting is on.
    auth_rate_limit_per_minute: int = 10

    database_url: str = "sqlite+aiosqlite:///./data/aura.db"
    # Signs session JWTs. Empty means "generate a random one for this process" —
    # fine for local dev (see get_settings), but every restart invalidates every
    # signed-in session, and it obviously can't be shared across instances. Set
    # a real value before deploying anywhere.
    jwt_secret: str = ""
    jwt_expires_minutes: int = 60 * 24 * 30  # 30 days

    @property
    def has_anthropic_key(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_spotify_credentials(self) -> bool:
        return bool(self.spotify_client_id and self.spotify_client_secret)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.jwt_secret:
        settings.jwt_secret = secrets.token_hex(32)
        logger.warning(
            "JWT_SECRET not set — generated a random one for this process. "
            "Every restart will sign everyone out. Set JWT_SECRET in .env before deploying."
        )
    if not settings.token_encryption_key:
        from cryptography.fernet import Fernet

        settings.token_encryption_key = Fernet.generate_key().decode()
        logger.warning(
            "TOKEN_ENCRYPTION_KEY not set — generated a random one for this process. "
            "Every restart will force reconnecting Spotify accounts. Set "
            "TOKEN_ENCRYPTION_KEY in .env before deploying."
        )
    return settings
