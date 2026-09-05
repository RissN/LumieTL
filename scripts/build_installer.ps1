# Compile Inno Setup Installer
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

$InnoSetupCandidates = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

$InnoSetup = $InnoSetupCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $InnoSetup) {
    Write-Warning "Inno Setup 6 tidak ditemukan di sistem lokal."
    Write-Host "Unduh dan instal Inno Setup 6 dari https://jrsoftware.org/isinfo.php untuk mengompilasi installer." -ForegroundColor Yellow
    exit 1
}

Write-Host ">>> Mengompilasi installer dengan Inno Setup..." -ForegroundColor Cyan
& $InnoSetup ".\installer\setup.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ">>> Installer siap di folder dist\LumieTL_Setup_v1.0.0.exe" -ForegroundColor Green
} else {
    Write-Error ">>> Kompilasi installer gagal!"
}
