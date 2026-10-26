"""One row per user per calendar day they've chosen to annotate.

Deliberately independent of the Spotify connection: works whether or not the
user has connected Spotify, since it's the user's own words, not derived
data. The Memories page merges this with real recently-played tracks for the
same date when a Spotify connection exists.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Memory(Base):
    __tablename__ = "memories"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_memory_user_date"),)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[str] = mapped_column(String(10))  # ISO "YYYY-MM-DD"
    note: Mapped[str] = mapped_column(Text)
    mood: Mapped[str | None] = mapped_column(String(50), nullable=True)
