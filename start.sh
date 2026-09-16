#!/bin/bash
echo "============================================"
echo "  LumieTL - Manga/Manhwa Auto-Translator"
echo "============================================"
echo ""

cd "$(dirname "$0")"

if [ ! -f "venv/bin/activate" ]; then
    echo "[!] Virtual environment not found."
    echo "    Run: python3.11 -m venv venv"
    echo "    Then: venv/bin/pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate
echo "[*] LumieTL running at http://localhost:18420"
uvicorn main:app --host 127.0.0.1 --port 18420
