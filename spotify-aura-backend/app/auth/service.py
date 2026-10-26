"""Signup/signin — repository-free since these queries are small and one-shot."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import TasteProfile, User
from app.auth.schemas import SigninRequest, SignupRequest, TasteProfileIn
from app.auth.security import create_access_token, hash_password, verify_password
from app.errors import ConflictError, UnauthorizedError


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def signup(self, payload: SignupRequest) -> tuple[User, str]:
        existing = await self.session.execute(
            select(User).where(User.email == payload.email.lower())
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictError("An account with this email already exists.")

        user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
        self.session.add(user)
        await self.session.flush()
        return user, create_access_token(user.id)

    async def signin(self, payload: SigninRequest) -> tuple[User, str]:
        result = await self.session.execute(
            select(User).where(User.email == payload.email.lower())
        )
        user = result.scalar_one_or_none()
        # Same error for "no such user" and "wrong password" — don't let a
        # login form confirm which emails have accounts.
        if user is None or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")
        return user, create_access_token(user.id)

    async def get_taste(self, user_id: str) -> TasteProfile | None:
        result = await self.session.execute(
            select(TasteProfile).where(TasteProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def set_taste(self, user_id: str, payload: TasteProfileIn) -> TasteProfile:
        existing = await self.get_taste(user_id)
        if existing is None:
            existing = TasteProfile(user_id=user_id)
            self.session.add(existing)
        existing.seed_artists = payload.seed_artists
        existing.seed_genres = payload.seed_genres
        existing.novelty = payload.novelty
        await self.session.flush()
        return existing
