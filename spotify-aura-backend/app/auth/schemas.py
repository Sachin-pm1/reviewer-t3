"""Auth + per-user taste-profile schemas."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _reject_over_72_bytes(password: str) -> str:
    # bcrypt only ever looks at the first 72 bytes of input and raises ValueError
    # on anything longer (reproduced directly against the installed bcrypt) —
    # not truncated silently, so this must be caught before hash_password() ever
    # sees it. A char-count limit alone doesn't guarantee this: multi-byte UTF-8
    # (accents, emoji) can blow past 72 bytes well under 72 characters.
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password is too long (max 72 bytes).")
    return password


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)

    _reject_long_password = field_validator("password")(_reject_over_72_bytes)


class SigninRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def _assume_utc_if_naive(cls, value: object) -> object:
        # SQLite has no real timezone-aware column type, so SQLAlchemy hands back
        # a naive datetime on any read that didn't originate from this same
        # in-memory insert (this project always writes with datetime.now(UTC), so
        # naive-here always means UTC-with-the-label-stripped, never ambiguous).
        # Skipping this turned "signed up seconds ago" into "5h ago" client-side
        # the first time this exact bug showed up, in the main platform's schemas.
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class TasteProfileIn(BaseModel):
    seed_artists: list[str] = Field(default_factory=list, max_length=10)
    seed_genres: list[str] = Field(default_factory=list, max_length=10)
    novelty: int = Field(default=50, ge=0, le=100)


class TasteProfileOut(TasteProfileIn):
    pass
