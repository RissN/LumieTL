"""LumieTL — FastAPI application entry point.

Registers middleware, mounts API routers, serves the Vue frontend,
and initialises shared dependencies.
"""

import asyncio
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from core.config import (
    APP_DATA_DIR,
    APP_VERSION,
    HISTORY_DB,
    KEYS_FILE,
    MAX_CONCURRENT_TRANSLATIONS,
    MODEL_DIR,
    OUTPUT_DIR,
)
from core.batch_processor import BatchProcessor
from core.history_manager import HistoryManager
from middleware.csrf import CSRFMiddleware
from middleware.rate_limit import RateLimitMiddleware
from security.keystore import Keystore
from utils.logger import audit

from api import history, models, settings, translate

# ---------------------------------------------------------------------------
# Ensure data directories exist
# ---------------------------------------------------------------------------
for directory in [APP_DATA_DIR, MODEL_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Shared dependencies
# ---------------------------------------------------------------------------
_history_mgr = HistoryManager(HISTORY_DB)
_keystore = Keystore(KEYS_FILE)
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TRANSLATIONS)
_batch_proc = BatchProcessor(_semaphore, _history_mgr, _keystore)

# Inject into API modules
translate.init_translate_deps(_history_mgr, _keystore, _batch_proc)
history.init_history_deps(_history_mgr)
settings.init_settings_deps(_keystore)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="LumieTL",
    version=APP_VERSION,
    docs_url=None,   # Swagger disabled in production
    redoc_url=None,
)

# Middleware (executed in reverse registration order)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:18420", "http://127.0.0.1:18420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(translate.router, prefix="/api/translate", tags=["translate"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

# ---------------------------------------------------------------------------
# App info endpoint
# ---------------------------------------------------------------------------

@app.get("/api/info")
async def app_info() -> dict:
    """Return basic application metadata."""
    return {
        "name": "LumieTL",
        "version": APP_VERSION,
    }


# ---------------------------------------------------------------------------
# Serve Vue frontend (built static files)
# ---------------------------------------------------------------------------
FRONTEND_DIST = Path(__file__).parent / "static"

if FRONTEND_DIST.exists():
    # Serve static assets (JS, CSS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str) -> FileResponse:
        """Serve the Vue SPA — all non-API routes return index.html."""
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")

# ---------------------------------------------------------------------------
# Startup audit
# ---------------------------------------------------------------------------
audit("app_start", f"version={APP_VERSION}")

# ---------------------------------------------------------------------------
# Direct execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    from core.config import WEB_PORT

    uvicorn.run(app, host="127.0.0.1", port=WEB_PORT, log_level="warning")
