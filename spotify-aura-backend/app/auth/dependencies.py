"""FastAPI dependency that resolves the current user from a bearer token."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.auth.models import User
from app.auth.security import decode_access_token
from app.database import get_session
from app.errors import UnauthorizedError

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Sign in required.")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise UnauthorizedError("Session expired or invalid — sign in again.")
    user = await session.get(User, user_id)
    if user is None:
        raise UnauthorizedError("Session expired or invalid — sign in again.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
