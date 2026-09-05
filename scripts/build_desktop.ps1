# Build LumieTL Desktop (.exe)
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

Write-Host ">>> Memeriksa environment Python..." -ForegroundColor Cyan
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
}

Write-Host ">>> Memulai packaging dengan PyInstaller..." -ForegroundColor Cyan
pyinstaller LumieTL.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host ">>> Build berhasil selesai: dist\LumieTL\" -ForegroundColor Green
} else {
    Write-Error ">>> Build Desktop gagal!"
    exit 1
}
