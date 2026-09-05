"""Rate limiting utilities for translation engines and API endpoints."""

import time
from collections import deque
from threading import Lock


class RateLimiter:
    """
    Thread-safe sliding-window / token bucket rate limiter to prevent
    abuse and avoid 429 quota exhaustion on external translation APIs.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: deque[float] = deque()
        self._lock = Lock()

    def wait_if_needed(self) -> float:
        """
        Check request quota, sleeping if necessary until a slot becomes available.
        Returns the duration waited in seconds.
        """
        waited = 0.0
        with self._lock:
            now = time.time()
            # Evict timestamps outside the sliding window
            while self.requests and self.requests[0] < now - self.window:
                self.requests.popleft()

            if len(self.requests) >= self.max_requests:
                sleep_time = self.window - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    waited = sleep_time

            self.requests.append(time.time())
        return waited

    def is_allowed(self) -> bool:
        """Non-blocking check if a request can currently proceed."""
        with self._lock:
            now = time.time()
            while self.requests and self.requests[0] < now - self.window:
                self.requests.popleft()
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

    def reset(self) -> None:
        """Clear the history of requests."""
        with self._lock:
            self.requests.clear()


# Shared instances for translation engines
RATE_LIMITERS: dict[str, RateLimiter] = {
    "google": RateLimiter(max_requests=30, window_seconds=60),
    "deepl": RateLimiter(max_requests=50, window_seconds=60),
    "openai": RateLimiter(max_requests=20, window_seconds=60),
}
