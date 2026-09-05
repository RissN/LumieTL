"""LumieTL Single Runner.

Menjalankan backend FastAPI yang langsung menyajikan antarmuka Vue 3.
Penggunaan:
    python run.py
"""

import os
import sys
from pathlib import Path

# Pastikan root workspace berada di sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import WEB_HOST, WEB_PORT
from utils.logger import setup_logger

logger = setup_logger()


def main():
    import uvicorn

    print(f"==================================================")
    print(f"   LumieTL - Manga/Manhwa/Manhua Auto-Translator")
    print(f"   Web Monolith (FastAPI + Vue 3)")
    print(f"==================================================")
    print(f"URL: http://{WEB_HOST}:{WEB_PORT}")
    print(f"Tekan Ctrl+C untuk menghentikan server.\n")

    uvicorn.run("backend.main:app", host=WEB_HOST, port=WEB_PORT, reload=False, log_level="info")


if __name__ == "__main__":
    main()
