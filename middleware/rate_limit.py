"""Rate limiting middleware — per-IP sliding window."""

from collections import defaultdict, deque
import time

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class IPRateLimiter:
    """In-memory sliding-window rate limiter keyed by client IP."""

    def __init__(self, max_requests: int = 20, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        q = self._store[ip]
        while q and q[0] < now - self.window:
            q.popleft()
        if len(q) >= self.max_requests:
            return False
        q.append(now)
        return True


_ip_limiter = IPRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that enforces per-IP rate limits."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        if not _ip_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait.",
            )
        return await call_next(request)
