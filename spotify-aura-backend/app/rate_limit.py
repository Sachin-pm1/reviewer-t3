"""Minimal per-IP rate limiting.

Same reasoning as the parent repo's app/core/rate_limit.py: this endpoint is
public, unauthenticated, and triggers a real Claude call plus real Spotify API
calls per request, so it needs a floor against a runaway script even though
this is a single-instance deployment with no shared state to coordinate.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.responses import JSONResponse

from app.config import get_settings


class RateLimiter:
    """Fixed-key sliding-window limiter. Pure and clock-injectable for testing."""

    def __init__(self, limit: int, window_seconds: float = 60.0) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        bucket = self._hits[key]
        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


_limiter = RateLimiter(limit=1)  # replaced with the real configured limit below

# Separate, stricter bucket for signin/signup specifically: bcrypt makes each
# guess expensive already, but the general per-IP limit (30/min, shared with
# every other route) still leaves room for real credential-stuffing volume.
# Keyed apart from _limiter so hammering /auth/signin can't be hidden inside a
# few legitimate /companion/chat calls, or vice versa.
_auth_limiter = RateLimiter(limit=1)
_AUTH_PATHS = {"/auth/signin", "/auth/signup"}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _blocked_response() -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limited",
                "message": "Too many requests — try again in a minute.",
            }
        },
    )


def check_rate_limit(request: Request) -> JSONResponse | None:
    """Returns a 429 response if ``request`` should be blocked, else None.

    Called from inside the single app-wide middleware, not registered as a
    second BaseHTTPMiddleware layer — see the parent repo's rate_limit.py for
    why stacking two of those broke clean error responses.
    """
    settings = get_settings()
    limit = settings.rate_limit_per_minute
    if limit <= 0:
        return None  # 0 disables rate limiting entirely (tests do this)

    ip = _client_ip(request)

    if request.url.path in _AUTH_PATHS:
        auth_limit = settings.auth_rate_limit_per_minute
        if _auth_limiter.limit != auth_limit:
            _auth_limiter.limit = auth_limit
        if not _auth_limiter.allow(ip):
            return _blocked_response()

    if _limiter.limit != limit:
        _limiter.limit = limit
    if not _limiter.allow(ip):
        return _blocked_response()
    return None
