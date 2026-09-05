"""HTTP Basic Authentication security middleware for self-hosted instances."""

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from core.config import WEB_AUTH_ENABLED, WEB_AUTH_PASS, WEB_AUTH_USER

security = HTTPBasic(auto_error=False)


def verify_auth(credentials: HTTPBasicCredentials | None = Depends(security)) -> None:
    """Validate HTTP Basic Authentication credentials when auth is enabled."""
    if not WEB_AUTH_ENABLED:
        return

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentikasi diperlukan",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Secure timing-attack resistant comparison
    user_ok = secrets.compare_digest(
        credentials.username.encode("utf-8"), WEB_AUTH_USER.encode("utf-8")
    )
    pass_ok = secrets.compare_digest(
        credentials.password.encode("utf-8"), WEB_AUTH_PASS.encode("utf-8")
    )

    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kredensial tidak valid",
            headers={"WWW-Authenticate": "Basic"},
        )
