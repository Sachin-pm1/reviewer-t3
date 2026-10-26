"""Tests for the rate limiter — against its own isolated instances, with an injected
clock, so this never touches the shared app/client fixtures other tests use (those
would otherwise accumulate hits across the whole test run and fail unpredictably)."""

from __future__ import annotations

from app.core.rate_limit import RateLimiter


def test_allows_requests_within_the_limit():
    limiter = RateLimiter(limit=3, window_seconds=60)
    assert limiter.allow("ip-a", now=0.0)
    assert limiter.allow("ip-a", now=1.0)
    assert limiter.allow("ip-a", now=2.0)


def test_blocks_once_the_limit_is_exceeded():
    limiter = RateLimiter(limit=3, window_seconds=60)
    for t in (0.0, 1.0, 2.0):
        assert limiter.allow("ip-a", now=t)
    assert limiter.allow("ip-a", now=3.0) is False


def test_old_hits_fall_out_of_the_window():
    limiter = RateLimiter(limit=2, window_seconds=60)
    assert limiter.allow("ip-a", now=0.0)
    assert limiter.allow("ip-a", now=1.0)
    assert limiter.allow("ip-a", now=2.0) is False  # window still full
    # 61s later the first two hits have aged out of the 60s window.
    assert limiter.allow("ip-a", now=61.5)


def test_keys_are_independent():
    limiter = RateLimiter(limit=1, window_seconds=60)
    assert limiter.allow("ip-a", now=0.0)
    assert limiter.allow("ip-a", now=0.1) is False
    assert limiter.allow("ip-b", now=0.1) is True  # different key, own budget
