"""One row per app-account user who has linked a real Spotify account via the
Authorization Code flow. Tokens are stored encrypted at rest (see crypto.py) —
never in plaintext, unlike the app's own session JWTs which are never persisted."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SpotifyConnection(Base):
    __tablename__ = "spotify_connections"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    spotify_user_id: Mapped[str] = mapped_column(String(64))
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_token_encrypted: Mapped[str] = mapped_column(Text)
    refresh_token_encrypted: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String(500), default="")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
