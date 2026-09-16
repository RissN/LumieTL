"""Rate limiting middleware — per-IP sliding window."""

from collections import defaultdict, deque
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response


class IPRateLimiter:
    """In-memory sliding-window rate limiter keyed by client IP."""

    def __init__(self, max_requests: int = 1200, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, ip: str) -> bool:
        # Localhost / internal traffic is always allowed without throttling
        if ip in {"127.0.0.1", "::1", "localhost", "unknown", "testclient"}:
            return True

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
        # Exempt static assets and polling endpoints from rate limit checks
        path = request.url.path
        if (
            path.startswith("/assets")
            or path.startswith("/api/models/download")
            or path.startswith("/api/translate/batch")
            or path == "/favicon.ico"
        ):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        if not _ip_limiter.is_allowed(client_ip):
            # Return JSONResponse directly rather than raising HTTPException inside middleware,
            # which would cause Starlette to crash with a 500 Internal Server Error.
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please wait."},
            )
        return await call_next(request)
