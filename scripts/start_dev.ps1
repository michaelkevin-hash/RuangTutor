# scripts/start_dev.ps1
# Jalankan semua server RuangTutor dalam satu klik
# Usage (dari folder RuangTutor): .\scripts\start_dev.ps1

$ROOT         = Split-Path $PSScriptRoot -Parent
$LANGFLOW_EXE = "C:\Users\micha\AppData\Local\Programs\Python\Python312\Scripts\langflow.exe"
$NGROK_EXE    = "C:\Users\micha\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"
$UVICORN_EXE  = "C:\Users\micha\AppData\Local\Programs\Python\Python312\Scripts\uvicorn.exe"
$VENV_PYTHON  = "$ROOT\.venv\Scripts\python.exe"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   RuangTutor - Dev Startup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Validasi file .env
if (-not (Test-Path "$ROOT\.env")) {
    Write-Host "[ERROR] .env tidak ditemukan di $ROOT" -ForegroundColor Red
    Write-Host "  Jalankan: Copy-Item .env.example .env  lalu isi nilainya" -ForegroundColor Yellow
    exit 1
}

# Baca WEBHOOK_URL dari .env
$webhookUrl = (Get-Content "$ROOT\.env" | Where-Object { $_ -match "^WEBHOOK_URL=" }) -replace "^WEBHOOK_URL=",""
if ($webhookUrl -like "*your-public-domain*" -or [string]::IsNullOrWhiteSpace($webhookUrl)) {
    Write-Host "[WARN] WEBHOOK_URL belum diisi di .env" -ForegroundColor Yellow
    Write-Host "       Setelah ngrok jalan, salin HTTPS URL-nya dan update WEBHOOK_URL di .env" -ForegroundColor Yellow
    Write-Host ""
}

# ── Terminal 1: Langflow ──────────────────────────────────────────────────────
Write-Host "[1/3] Membuka Langflow..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command",
    "Write-Host '=== TERMINAL 1: Langflow AI Backend ===' -ForegroundColor Cyan;
     Write-Host 'Buka http://127.0.0.1:7860 setelah siap' -ForegroundColor Yellow;
     Write-Host '';
     & '$LANGFLOW_EXE' run"

Start-Sleep -Seconds 2

# ── Terminal 2: ngrok ────────────────────────────────────────────────────────
Write-Host "[2/3] Membuka ngrok tunnel..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command",
    "Write-Host '=== TERMINAL 2: ngrok Tunnel ===' -ForegroundColor Cyan;
     Write-Host 'Salin HTTPS Forwarding URL, lalu:' -ForegroundColor Yellow;
     Write-Host '  1. Update WEBHOOK_URL di .env' -ForegroundColor Yellow;
     Write-Host '  2. Restart Terminal 3 (FastAPI)' -ForegroundColor Yellow;
     Write-Host '';
     & '$NGROK_EXE' http 8000"

Start-Sleep -Seconds 2

# ── Terminal 3: FastAPI ──────────────────────────────────────────────────────
Write-Host "[3/3] Membuka FastAPI server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command",
    "Write-Host '=== TERMINAL 3: FastAPI Webhook Server ===' -ForegroundColor Cyan;
     Write-Host 'Tunggu Langflow siap dulu (~30 detik), lalu server ini auto-register webhook' -ForegroundColor Yellow;
     Write-Host '';
     cd '$ROOT';
     & '$UVICORN_EXE' main:app --reload --port 8000"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host " 3 terminal terbuka!" -ForegroundColor Green
Write-Host ""
Write-Host " Urutan yang benar:" -ForegroundColor Yellow
Write-Host "  1. Tunggu Terminal 1 (Langflow) tampilkan: 'Application startup complete'"
Write-Host "  2. Lihat Terminal 2 (ngrok) - salin HTTPS URL (contoh: https://abc123.ngrok-free.app)"
Write-Host "  3. Edit .env: WEBHOOK_URL=https://abc123.ngrok-free.app"
Write-Host "  4. Restart Terminal 3 (tutup lalu jalankan lagi)"
Write-Host "  5. Test bot: https://t.me/RuangTutor_bot"
Write-Host ""
Write-Host " Verifikasi sistem:"
Write-Host "  `$env:PYTHONIOENCODING='utf-8'; .venv\Scripts\python tests/test_setup.py"
Write-Host "=============================================" -ForegroundColor Green
