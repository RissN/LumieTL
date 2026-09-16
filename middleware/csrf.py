"""CSRF protection middleware.

Blocks mutating requests (POST, PUT, DELETE) when the ``Origin``
header does not match the ``Host`` header — a simple but effective
defense against cross-site request forgery for same-origin apps.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

_SAFE_METHODS: frozenset[str] = frozenset({"GET", "HEAD", "OPTIONS"})


class CSRFMiddleware(BaseHTTPMiddleware):
    """Reject cross-origin mutating requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method not in _SAFE_METHODS:
            origin = request.headers.get("origin", "")
            host = request.headers.get("host", "")
            if origin:
                # Strip scheme and trailing path from origin
                origin_host = (
                    origin.replace("https://", "")
                    .replace("http://", "")
                    .split("/")[0]
                )
                if origin_host != host:
                    raise HTTPException(
                        status_code=403,
                        detail="CSRF check failed",
                    )
        return await call_next(request)
