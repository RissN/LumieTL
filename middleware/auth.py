"""Optional HTTP Basic authentication middleware.

Enabled via environment variables:
    LUMIETL_AUTH_ENABLED=true
    LUMIETL_AUTH_USER=admin
    LUMIETL_AUTH_PASS=secret
"""

import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from core.config import WEB_AUTH_ENABLED, WEB_AUTH_USER, WEB_AUTH_PASS

_security = HTTPBasic(auto_error=False)


def verify_auth(
    credentials: HTTPBasicCredentials | None = Depends(_security),
) -> None:
    """FastAPI dependency that enforces basic auth when enabled.

    Usage::

        @router.get("/protected", dependencies=[Depends(verify_auth)])
        async def protected_route(): ...
    """
    if not WEB_AUTH_ENABLED:
        return

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    user_ok = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        WEB_AUTH_USER.encode("utf-8"),
    )
    pass_ok = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        WEB_AUTH_PASS.encode("utf-8"),
    )

    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
