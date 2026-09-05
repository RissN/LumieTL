"""FastAPI application entry point for LumieTL Web."""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import APP_DATA_DIR, MODEL_DIR, WEB_HOST, WEB_PORT, ensure_directories
from utils.logger import setup_logger
from backend.api import history, models, settings, translate
from backend.middleware.rate_limit import RateLimitMiddleware

logger = setup_logger()
ensure_directories()

# Detect development vs production mode
IS_DEV = os.environ.get("LUMIETL_DEV", "false").lower() == "true"

app = FastAPI(
    title="LumieTL API",
    version="1.0.0",
    docs_url="/docs" if IS_DEV else None,
    redoc_url="/redoc" if IS_DEV else None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Register API routers
app.include_router(translate.router, prefix="/api/translate", tags=["translate"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])


# Static frontend mounting (Vue 3 Single Page Application)
def _find_frontend_dist() -> Path | None:
    candidates = [
        Path(__file__).parent / "frontend_dist",
        PROJECT_ROOT / "frontend" / "dist",
    ]
    for c in candidates:
        if c.exists() and (c / "index.html").exists():
            return c
    return None


dist_dir = _find_frontend_dist()
if dist_dir:
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
    logger.info("Serving Vue 3 frontend from %s", dist_dir)
else:
    @app.get("/")
    async def index():
        return {
            "name": "LumieTL Web Monolith",
            "version": "1.0.0",
            "status": "online",
            "message": "Frontend belum dikompilasi. Jalankan `npm run build` di folder frontend.",
        }


def run_server():
    """Start uvicorn ASGI server."""
    import uvicorn

    logger.info("Starting LumieTL Web Server at http://%s:%d", WEB_HOST, WEB_PORT)
    uvicorn.run(app, host=WEB_HOST, port=WEB_PORT, log_level="info")


if __name__ == "__main__":
    run_server()
