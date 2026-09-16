@echo off
echo ============================================
echo   LumieTL - Manga/Manhwa Auto-Translator
echo ============================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found.
    echo     Run: py -3.11 -m venv venv
    echo     Then: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo [*] Starting LumieTL on http://localhost:18420
start "" http://localhost:18420
uvicorn main:app --host 127.0.0.1 --port 18420
pause
