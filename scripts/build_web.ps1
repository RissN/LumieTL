# Build and Package LumieTL Web Monolith
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

Write-Host ">>> [1/2] Mengompilasi frontend Vue 3..." -ForegroundColor Cyan
if (-not (Test-Path "frontend\node_modules")) {
    npm --prefix frontend install
}
npm --prefix frontend run build
if ($LASTEXITCODE -ne 0) {
    Write-Error ">>> Kompilasi frontend Vue 3 gagal!"
    exit 1
}

Write-Host ">>> [2/2] Mengemas LumieTL Web Monolith..." -ForegroundColor Cyan
$releaseDir = "release\LumieTL_Web"

if (Test-Path $releaseDir) {
    Remove-Item $releaseDir -Recurse -Force
}
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

Copy-Item "backend" -Destination $releaseDir -Recurse
Copy-Item "core" -Destination $releaseDir -Recurse
Copy-Item "security" -Destination $releaseDir -Recurse
Copy-Item "utils" -Destination $releaseDir -Recurse
Copy-Item "requirements.txt" -Destination $releaseDir

Set-Content -Path "$releaseDir\start.bat" -Value "uvicorn backend.main:app --host 127.0.0.1 --port 18420"
Set-Content -Path "$releaseDir\start.sh" -Value "uvicorn backend.main:app --host 127.0.0.1 --port 18420"

Write-Host ">>> Paket LumieTL Web Monolith selesai dibuat di $releaseDir!" -ForegroundColor Green
Write-Host "    Jalankan server dengan: cd $releaseDir; uvicorn backend.main:app --host 127.0.0.1 --port 18420" -ForegroundColor Yellow
