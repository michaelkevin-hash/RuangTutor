# scripts/install_tesseract.ps1
# Download dan install Tesseract OCR untuk Windows
# Jalankan sebagai Administrator: 
#   Start-Process powershell -Verb RunAs -ArgumentList "-File .\scripts\install_tesseract.ps1"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Install Tesseract OCR (Windows)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Cek apakah sudah terinstall
$tesseractPath = Get-Command tesseract -ErrorAction SilentlyContinue
if ($tesseractPath) {
    $version = & tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "✅ Tesseract sudah terinstall: $version" -ForegroundColor Green
    Write-Host ""
    
    # Cek bahasa Indonesia
    $langs = & tesseract --list-langs 2>&1
    if ($langs -match "ind") {
        Write-Host "✅ Bahasa Indonesia (ind) tersedia" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Bahasa Indonesia belum ada." -ForegroundColor Yellow
        Write-Host "   Download language pack dari:" -ForegroundColor Yellow
        Write-Host "   https://github.com/tesseract-ocr/tessdata/blob/main/ind.traineddata" -ForegroundColor Yellow
        Write-Host "   Simpan ke: C:\Program Files\Tesseract-OCR\tessdata\" -ForegroundColor Yellow
    }
    exit 0
}

Write-Host "Tesseract belum terinstall. Memulai download..." -ForegroundColor Yellow
Write-Host ""

$installerUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.5.0.20241111/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
$installerPath = "$env:TEMP\tesseract-installer.exe"

Write-Host "Downloading dari: $installerUrl"
Write-Host "Ke: $installerPath"
Write-Host ""

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✅ Download selesai!" -ForegroundColor Green
} catch {
    Write-Host "❌ Download gagal: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Download manual dari:" -ForegroundColor Yellow
    Write-Host "  https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Saat install, PASTIKAN centang:" -ForegroundColor Yellow
    Write-Host "  ☑ Additional language data → Indonesian" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Menjalankan installer..." -ForegroundColor Cyan
Write-Host "(Saat dialog muncul, centang 'Indonesian' di Additional Language Data!)" -ForegroundColor Yellow
Write-Host ""

Start-Process -FilePath $installerPath -Wait

# Tambahkan ke PATH
$tesseractInstallPath = "C:\Program Files\Tesseract-OCR"
if (Test-Path $tesseractInstallPath) {
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($currentPath -notlike "*Tesseract*") {
        [Environment]::SetEnvironmentVariable(
            "PATH",
            "$currentPath;$tesseractInstallPath",
            "Machine"
        )
        Write-Host "✅ Tesseract ditambahkan ke PATH sistem" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ Instalasi selesai!" -ForegroundColor Green
Write-Host "   Restart terminal kamu, lalu jalankan: tesseract --version" -ForegroundColor Yellow
