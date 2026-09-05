"""Hardened IP Rate Limiter middleware with TTL cleanup to prevent memory exhaustion."""

import time
from collections import deque
from threading import Lock
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class IPRateLimiter:
    """Sliding-window IP rate limiter with active memory pruning."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict[str, deque[float]] = {}
        self._last_prune = time.time()
        self._lock = Lock()

    def _prune_expired_entries(self, now: float) -> None:
        """Periodic garbage collection of stale IP queues to prevent memory leaks."""
        expired_ips = []
        for ip, timestamps in self._store.items():
            while timestamps and timestamps[0] < now - self.window:
                timestamps.popleft()
            if not timestamps:
                expired_ips.append(ip)

        for ip in expired_ips:
            del self._store[ip]

    def is_allowed(self, ip: str) -> bool:
        with self._lock:
            now = time.time()

            # Run cleanup every 60 seconds
            if now - self._last_prune > 60:
                self._prune_expired_entries(now)
                self._last_prune = now

            if ip not in self._store:
                self._store[ip] = deque()

            q = self._store[ip]
            while q and q[0] < now - self.window:
                q.popleft()

            if len(q) >= self.max_requests:
                return False

            q.append(now)
            return True


ip_limiter = IPRateLimiter(max_requests=40, window_seconds=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI/Starlette middleware enforcing per-IP rate limits."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Ignore static frontend files and favicon
        if request.url.path.startswith(("/assets", "/favicon.ico", "/index.html")) or request.url.path == "/":
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"

        if not ip_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Terlalu banyak permintaan (Rate limit exceeded). Silakan tunggu sebentar.",
            )

        return await call_next(request)
