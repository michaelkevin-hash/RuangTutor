# scripts/start_dev.ps1
# Jalankan semua server development dalam satu klik (Windows PowerShell)
# Usage: .\scripts\start_dev.ps1

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   RuangTutor – Development Startup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Cek .env ada
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] File .env tidak ditemukan!" -ForegroundColor Red
    Write-Host "  Jalankan dulu: Copy-Item .env.example .env" -ForegroundColor Yellow
    exit 1
}

# Cek venv ada
if (-not (Test-Path ".venv")) {
    Write-Host "[ERROR] Virtual environment tidak ditemukan!" -ForegroundColor Red
    Write-Host "  Jalankan dulu: python -m venv .venv && .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Buka 3 terminal baru:
# 1. Langflow
Write-Host "[1/3] Membuka terminal Langflow..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Write-Host 'TERMINAL 1: Langflow AI Backend' -ForegroundColor Cyan; `
     cd '$PWD'; `
     .venv\Scripts\activate; `
     pip show langflow > `$null 2>&1; `
     if (`$LASTEXITCODE -ne 0) { pip install langflow }; `
     langflow run"

Start-Sleep -Seconds 3

# 2. FastAPI
Write-Host "[2/3] Membuka terminal FastAPI..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Write-Host 'TERMINAL 2: FastAPI Webhook Server' -ForegroundColor Cyan; `
     cd '$PWD'; `
     .venv\Scripts\activate; `
     Write-Host 'Tunggu Langflow siap dulu (30 detik)...'; `
     Start-Sleep 30; `
     uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 2

# 3. ngrok
Write-Host "[3/3] Membuka terminal ngrok..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Write-Host 'TERMINAL 3: ngrok tunnel' -ForegroundColor Cyan; `
     Write-Host 'Salin HTTPS URL lalu update WEBHOOK_URL di .env' -ForegroundColor Yellow; `
     Write-Host ''; `
     ngrok http 8000"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host " 3 terminal sudah dibuka!" -ForegroundColor Green
Write-Host ""
Write-Host " Langkah selanjutnya:" -ForegroundColor Yellow
Write-Host "  1. Tunggu Langflow siap (terminal 1 menampilkan URL)"
Write-Host "  2. Salin HTTPS URL dari ngrok (terminal 3)"
Write-Host "  3. Update WEBHOOK_URL di .env dengan URL ngrok"
Write-Host "  4. Restart terminal FastAPI (terminal 2)"
Write-Host "  5. Test bot: https://t.me/RuangTutor_bot"
Write-Host ""
Write-Host " Jalankan test: .venv\Scripts\python tests/test_setup.py"
Write-Host "=============================================" -ForegroundColor Green
