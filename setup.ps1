# ============================================================================
#  Windows setup. Run from the project folder:
#      powershell -ExecutionPolicy Bypass -File .\setup.ps1
# ============================================================================

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "`n=== youtubebot setup ===`n" -ForegroundColor Cyan

# --- Python ---------------------------------------------------------------
$py = $null
foreach ($candidate in @("py -3.12", "py -3.11", "python")) {
    try {
        $ver = Invoke-Expression "$candidate --version" 2>$null
        if ($ver) { $py = $candidate; Write-Host "[ok] Python: $ver" -ForegroundColor Green; break }
    } catch {}
}
if (-not $py) {
    Write-Host "[!!] Python not found. Install it from https://python.org (3.12 recommended)" -ForegroundColor Red
    exit 1
}

# --- FFmpeg ---------------------------------------------------------------
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "[ok] ffmpeg: $((ffmpeg -version | Select-Object -First 1))" -ForegroundColor Green
} else {
    Write-Host "[..] ffmpeg missing - installing with winget" -ForegroundColor Yellow
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    Write-Host "[!!] Close and reopen PowerShell, then re-run this script." -ForegroundColor Yellow
    Write-Host "     (winget changes PATH, but this window will not see it.)" -ForegroundColor Yellow
    exit 0
}

# --- Virtual environment --------------------------------------------------
if (-not (Test-Path "venv")) {
    Write-Host "[..] creating virtual environment" -ForegroundColor Yellow
    Invoke-Expression "$py -m venv venv"
}
& ".\venv\Scripts\Activate.ps1"
Write-Host "[ok] venv activated: $((python --version))" -ForegroundColor Green

# --- Dependencies ---------------------------------------------------------
Write-Host "[..] installing dependencies" -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!!] pip install failed. If you are on Python 3.14, install 3.12 instead." -ForegroundColor Red
    exit 1
}
Write-Host "[ok] dependencies installed" -ForegroundColor Green

# --- Config ---------------------------------------------------------------
if (-not (Test-Path "config.yaml")) {
    Copy-Item "config.example.yaml" "config.yaml"
    Write-Host "[ok] created config.yaml - open it and set channel.topic + ai.gemini_api_key" -ForegroundColor Green
} else {
    Write-Host "[ok] config.yaml already exists" -ForegroundColor Green
}

# --- Credentials ----------------------------------------------------------
if (Test-Path "client_secret.json") {
    Write-Host "[ok] client_secret.json present" -ForegroundColor Green
} else {
    $found = Get-ChildItem -Path $HOME\Downloads -Filter "client_secret*.json" -ErrorAction SilentlyContinue |
             Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($found) {
        Copy-Item $found.FullName "client_secret.json"
        Write-Host "[ok] copied $($found.Name) -> client_secret.json" -ForegroundColor Green
    } else {
        Write-Host "[!!] client_secret.json missing." -ForegroundColor Red
        Write-Host "     Google Cloud Console -> APIs & Services -> Credentials ->"
        Write-Host "     your OAuth Desktop-app client -> Download JSON -> save it here"
        Write-Host "     as client_secret.json" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Next steps ===" -ForegroundColor Cyan
Write-Host "  notepad config.yaml          # set your topic and Gemini key"
Write-Host "  python main.py preflight     # check everything"
Write-Host "  python main.py auth          # one-time YouTube login"
Write-Host "  python main.py generate      # make a video"
Write-Host ""
