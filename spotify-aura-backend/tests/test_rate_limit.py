"""RateLimiter is pure and clock-injectable — test it directly rather than
through the ASGI app, so these stay isolated from every other test's requests
(which all appear to come from the same IP through the ASGI transport)."""

from __future__ import annotations

from app.rate_limit import RateLimiter


def test_allows_up_to_the_limit_then_blocks():
    limiter = RateLimiter(limit=3, window_seconds=60)
    assert limiter.allow("1.2.3.4", now=0)
    assert limiter.allow("1.2.3.4", now=1)
    assert limiter.allow("1.2.3.4", now=2)
    assert not limiter.allow("1.2.3.4", now=3)


def test_old_hits_fall_out_of_the_window():
    limiter = RateLimiter(limit=1, window_seconds=60)
    assert limiter.allow("1.2.3.4", now=0)
    assert not limiter.allow("1.2.3.4", now=30)
    assert limiter.allow("1.2.3.4", now=61)  # first hit is now outside the window


def test_keys_are_independent():
    limiter = RateLimiter(limit=1, window_seconds=60)
    assert limiter.allow("1.2.3.4", now=0)
    assert limiter.allow("5.6.7.8", now=0)  # different key, own budget
    assert not limiter.allow("1.2.3.4", now=1)
