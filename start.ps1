# start.ps1 — launch the Reviewer platform (API + dashboard) and the
# standalone Spotify Aura MVP (its own API + frontend), each in its own window.
# Usage (from the project root):  .\start.ps1
# Requires this repo's venv (.venv\Scripts\python.exe), spotify-aura-backend's
# own venv, and Node (npm) to be installed in both frontends.

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

# Kill anything already on these ports so re-runs never fail
foreach ($port in 8000, 3000, 8010, 3010) {
    $pids = (netstat -ano 2>$null | Select-String ":$port\s") -replace '.*\s(\d+)$','$1' | Sort-Object -Unique
    foreach ($p in $pids) {
        if ($p -match '^\d+$') {
            Stop-Process -Id ([int]$p) -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host ""
Write-Host "=== AI Product Intelligence Platform ===" -ForegroundColor Cyan
Write-Host ""

# --- Reviewer platform: FastAPI backend (new window) ---
$apiCmd = "Set-Location '$root'; Write-Host 'Reviewer API starting...' -ForegroundColor Green; & '.venv\Scripts\python.exe' -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCmd

Start-Sleep 2

# --- Reviewer platform: Next.js dashboard (new window) ---
$feCmd = "Set-Location '$root\frontend'; Write-Host 'Reviewer dashboard starting...' -ForegroundColor Green; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $feCmd

# --- Spotify Aura MVP: FastAPI backend, its own venv (new window) ---
$auraApiCmd = "Set-Location '$root\spotify-aura-backend'; Write-Host 'Spotify Aura API starting...' -ForegroundColor Green; & '.venv\Scripts\python.exe' -m uvicorn app.main:app --reload --port 8010"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $auraApiCmd

Start-Sleep 2

# --- Spotify Aura MVP: Next.js frontend, its own project (new window) ---
$auraFeCmd = "Set-Location '$root\spotify-aura-frontend'; Write-Host 'Spotify Aura UI starting...' -ForegroundColor Green; npm run dev -- --port 3010"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $auraFeCmd

Write-Host "[1/4] Reviewer API       window opened  ->  http://localhost:8000" -ForegroundColor Green
Write-Host "[2/4] Reviewer dashboard window opened  ->  http://localhost:3000" -ForegroundColor Green
Write-Host "[3/4] Spotify Aura API   window opened  ->  http://localhost:8010" -ForegroundColor Green
Write-Host "[4/4] Spotify Aura UI    window opened  ->  http://localhost:3010" -ForegroundColor Green
Write-Host ""
Write-Host "  Reviewer dashboard : http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Reviewer API docs  : http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  Spotify Aura MVP   : http://localhost:3010" -ForegroundColor Yellow
Write-Host "  Spotify Aura docs  : http://localhost:8010/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Four terminal windows have opened. Close them to stop the servers." -ForegroundColor Gray
Write-Host "Waiting for both frontends to be ready..." -ForegroundColor Gray

function Wait-ForPort($port) {
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep 2
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            if ($r.StatusCode -eq 200) { return $true }
        } catch { }
    }
    return $false
}

$reviewerReady = Wait-ForPort 3000
$auraReady = Wait-ForPort 3010

Write-Host ""
if ($reviewerReady) {
    Write-Host "Reviewer dashboard is UP at http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "Reviewer dashboard is still starting — check its window for progress." -ForegroundColor Yellow
}
if ($auraReady) {
    Write-Host "Spotify Aura UI is UP at http://localhost:3010" -ForegroundColor Cyan
} else {
    Write-Host "Spotify Aura UI is still starting — check its window for progress." -ForegroundColor Yellow
}
