"""Minimal per-IP rate limiting.

Single-instance, in-memory sliding window — no Redis, no new dependency. That's
enough for this deployment's actual scale (one Render instance, no shared state
across processes needed) and exists for one specific reason: the analyze and chat
endpoints are public and unauthenticated, so once this is deployed with a real
ANTHROPIC_API_KEY behind it, anything reachable at the URL can run up real API
costs with a tight request loop. This raises that bar; it is not a substitute for
real auth if this ever needs to withstand a determined attacker rather than a
runaway script or bot.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings


class RateLimiter:
    """Fixed-key sliding-window limiter. Pure and clock-injectable for testing."""

    def __init__(self, limit: int, window_seconds: float = 60.0) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, now: float | None = None) -> bool:
        """Record a hit for ``key`` and return whether it's within the limit."""
        now = time.monotonic() if now is None else now
        bucket = self._hits[key]
        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


# One process-wide limiter backing the live app. Tests exercise the RateLimiter
# class directly instead of this instance, so they stay isolated from each other
# and from whatever the ASGI test client's apparent IP happens to be.
_limiter = RateLimiter(limit=1)  # replaced with the real configured limit below


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request) -> JSONResponse | None:
    """Returns a 429 response if ``request`` should be blocked, else None.

    A plain function called from inside the app's single existing
    ``@app.middleware("http")``, not a second one of its own — stacking multiple
    BaseHTTPMiddleware-based middlewares is a known Starlette footgun: when an
    exception occurs deep in the stack, re-propagating it through more than one
    such layer can stop the clean JSON error response from actually reaching the
    client (reproduced directly: a downstream ValidationError turned into a
    connection reset instead of the registered exception handler's 500 response,
    right after a second middleware layer was added here).
    """
    limit = get_settings().rate_limit_per_minute
    if limit <= 0:  # 0 disables it entirely (tests; anyone who wants it off)
        return None

    if _limiter.limit != limit:
        _limiter.limit = limit  # picks up config without needing a fresh instance

    if not _limiter.allow(_client_ip(request)):
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "rate_limited",
                    "message": "Too many requests — try again in a minute.",
                }
            },
        )
    return None
