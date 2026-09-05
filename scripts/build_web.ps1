# Build LumieTL Web package
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

Write-Host ">>> Membangun frontend Vue 3 + Tailwind..." -ForegroundColor Cyan
Set-Location "web\frontend"
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Error ">>> Gagal melakukan build frontend Vue!"
    exit 1
}

Write-Host ">>> Menyalin frontend dist ke backend/frontend_dist..." -ForegroundColor Cyan
Set-Location "..\.."
$targetDist = "web\backend\frontend_dist"
if (Test-Path $targetDist) {
    Remove-Item $targetDist -Recurse -Force
}
Copy-Item "web\frontend\dist" -Destination $targetDist -Recurse

Write-Host ">>> Web version siap dijalankan!" -ForegroundColor Green
Write-Host "    Jalankan perintah: .\venv\Scripts\python -m web.backend.main" -ForegroundColor Yellow
