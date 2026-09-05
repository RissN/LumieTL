# Package LumieTL Web Monolith
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

Write-Host ">>> Menyiapkan LumieTL Web Monolith..." -ForegroundColor Cyan
$releaseDir = "release\LumieTL_Web"

if (Test-Path $releaseDir) {
    Remove-Item $releaseDir -Recurse -Force
}
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

Copy-Item "web" -Destination $releaseDir -Recurse
Copy-Item "core" -Destination $releaseDir -Recurse
Copy-Item "security" -Destination $releaseDir -Recurse
Copy-Item "utils" -Destination $releaseDir -Recurse
Copy-Item "requirements-web.txt" -Destination "$releaseDir\requirements.txt"

Set-Content -Path "$releaseDir\start.bat" -Value "python -m web.backend.main"
Set-Content -Path "$releaseDir\start.sh" -Value "python -m web.backend.main"

Write-Host ">>> Paket LumieTL Web Monolith berhasil dibuat di $releaseDir!" -ForegroundColor Green
Write-Host "    Jalankan perintah: python -m web.backend.main" -ForegroundColor Yellow
