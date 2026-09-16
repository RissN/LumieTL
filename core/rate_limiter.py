"""Per-engine rate limiting with thread-safe sliding window."""

import time
from collections import deque
from threading import Lock

from core.config import ENGINE_RATE_LIMITS


class RateLimiter:
    """Sliding-window rate limiter.

    When the limit is reached, ``wait_if_needed()`` blocks the calling
    thread until a slot becomes available — requests are queued, not
    rejected.
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: deque[float] = deque()
        self._lock = Lock()

    def wait_if_needed(self) -> None:
        """Block until a request slot is available."""
        with self._lock:
            now = time.time()
            # Purge timestamps outside the current window
            while self.requests and self.requests[0] < now - self.window:
                self.requests.popleft()

            if len(self.requests) >= self.max_requests:
                sleep_time = self.window - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self.requests.append(time.time())


# Pre-built limiters for each translation engine
RATE_LIMITERS: dict[str, RateLimiter] = {
    engine: RateLimiter(
        max_requests=cfg["max_requests"],
        window_seconds=cfg["window_seconds"],
    )
    for engine, cfg in ENGINE_RATE_LIMITS.items()
}
