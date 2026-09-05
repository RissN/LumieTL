"""Unit tests for rate limiter."""

import time
from core.rate_limiter import RateLimiter


def test_rate_limiter_allows_under_limit():
    limiter = RateLimiter(max_requests=5, window_seconds=2)
    for _ in range(5):
        assert limiter.is_allowed() is True
    # 6th should be rejected
    assert limiter.is_allowed() is False


def test_rate_limiter_reset():
    limiter = RateLimiter(max_requests=2, window_seconds=10)
    assert limiter.is_allowed() is True
    assert limiter.is_allowed() is True
    assert limiter.is_allowed() is False

    limiter.reset()
    assert limiter.is_allowed() is True
