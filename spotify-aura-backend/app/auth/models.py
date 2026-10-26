"""Account + per-user taste-profile persistence."""

from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class TasteProfile(Base):
    """One row per user — replaces the browser-localStorage-only taste profile
    when the listener is signed in, so it follows them across devices."""

    __tablename__ = "taste_profiles"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    seed_artists: Mapped[list] = mapped_column(JSON, default=list)
    seed_genres: Mapped[list] = mapped_column(JSON, default=list)
    novelty: Mapped[int] = mapped_column(Integer, default=50)
