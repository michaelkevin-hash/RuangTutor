"""
Test suite untuk verifikasi semua komponen RuangTutor sebelum live.

Jalankan:
    python tests/test_setup.py

Setiap test memberi tahu apakah komponen sudah siap atau belum.
"""
import asyncio
import os
import sys
from pathlib import Path

# Tambahkan root project ke sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

PASS = "  ✅"
FAIL = "  ❌"
WARN = "  ⚠️ "

results = []


def check(name: str, passed: bool, message: str = ""):
    icon = PASS if passed else FAIL
    print(f"{icon} {name}" + (f"\n     → {message}" if message else ""))
    results.append(passed)


# ─────────────────────────────────────────────
# 1. Environment variables
# ─────────────────────────────────────────────
print("\n📋 [1] Environment Variables")

token = os.getenv("TELEGRAM_BOT_TOKEN", "")
check(
    "TELEGRAM_BOT_TOKEN",
    bool(token) and token != "***REMOVED***",
    "Token terisi. Ingat: jangan commit token asli ke Git!"
    if token else "Belum diisi di .env",
)

lf_url = os.getenv("LANGFLOW_API_URL", "")
check(
    "LANGFLOW_API_URL",
    bool(lf_url),
    lf_url or "Belum diisi di .env",
)

webhook = os.getenv("WEBHOOK_URL", "")
check(
    "WEBHOOK_URL",
    bool(webhook) and "your-public-domain" not in webhook,
    webhook or "Belum diisi – jalankan ngrok dulu lalu update .env",
)


# ─────────────────────────────────────────────
# 2. Python dependencies
# ─────────────────────────────────────────────
print("\n📦 [2] Python Dependencies")

deps = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("python-telegram-bot", "telegram"),
    ("httpx", "httpx"),
    ("python-dotenv", "dotenv"),
    ("Pillow", "PIL"),
    ("pytesseract", "pytesseract"),
]

for display_name, import_name in deps:
    try:
        __import__(import_name)
        check(display_name, True)
    except ImportError:
        check(display_name, False, f"pip install {display_name}")


# ─────────────────────────────────────────────
# 3. Tesseract binary
# ─────────────────────────────────────────────
print("\n🔤 [3] Tesseract OCR Binary")

try:
    import pytesseract

    # Set explicit path for Windows (from config or well-known default)
    tess_cmd = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if os.path.exists(tess_cmd):
        pytesseract.pytesseract.tesseract_cmd = tess_cmd

    version = pytesseract.get_tesseract_version()
    check("Tesseract binary", True, f"Version {version}")

    langs = pytesseract.get_languages()
    has_ind = "ind" in langs
    check(
        "Bahasa Indonesia (ind)",
        has_ind,
        "Tersedia" if has_ind
        else "Tidak ada. Download: https://github.com/tesseract-ocr/tessdata/raw/main/ind.traineddata → simpan ke C:\\Program Files\\Tesseract-OCR\\tessdata\\",
    )
except Exception as e:
    check("Tesseract binary", False,
          f"Tidak ditemukan. Download: https://github.com/UB-Mannheim/tesseract/wiki\n     Error: {e}")
    check("Bahasa Indonesia (ind)", False, "Tergantung Tesseract")


# ─────────────────────────────────────────────
# 4. Langflow connectivity
# ─────────────────────────────────────────────
print("\n🤖 [4] Langflow Connectivity")


async def test_langflow():
    import httpx

    url = os.getenv("LANGFLOW_API_URL", "http://127.0.0.1:7860/api/v1/run/741990f6-cf6e-4039-bcb6-1bf774dd91d7")
    api_key = os.getenv("LANGFLOW_API_KEY", "")
    headers = {"x-api-key": api_key} if api_key else {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                url,
                json={"output_type": "chat", "input_type": "chat", "input_value": "ping"},
                headers=headers,
            )
        if resp.status_code == 200:
            data = resp.json()
            text = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            return True, f"Langflow OK – sample reply: \"{text[:80]}...\""
        else:
            return False, f"HTTP {resp.status_code} – Langflow berjalan tapi ada error"
    except httpx.ConnectError:
        return False, "Tidak bisa connect. Pastikan `langflow run` sudah berjalan di terminal lain."
    except Exception as e:
        return False, f"Error: {e}"


lf_ok, lf_msg = asyncio.run(test_langflow())
check("Langflow reachable", lf_ok, lf_msg)


# ─────────────────────────────────────────────
# 5. FastAPI app import
# ─────────────────────────────────────────────
print("\n⚡ [5] FastAPI App Import")

try:
    from main import app
    check("main.py imports OK", True)
    check("FastAPI routes registered", len(app.routes) >= 3, f"{len(app.routes)} routes found")
except Exception as e:
    check("main.py imports OK", False, str(e))
    check("FastAPI routes registered", False, "Tidak bisa dicek karena import gagal")


# ─────────────────────────────────────────────
# 6. Telegram token format
# ─────────────────────────────────────────────
print("\n📱 [6] Telegram Bot Token Format")

import re
token_re = re.compile(r"^\d{8,10}:[A-Za-z0-9_-]{35}$")
token_val = os.getenv("TELEGRAM_BOT_TOKEN", "")
check(
    "Token format valid",
    bool(token_re.match(token_val)),
    "Format OK" if token_re.match(token_val) else "Format salah – cek kembali token dari @BotFather",
)


# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
total = len(results)
passed = sum(results)
failed = total - passed

print(f"\n{'='*50}")
print(f"  Hasil: {passed}/{total} checks passed")
if failed == 0:
    print("  🎉 Semua OK! Bot siap dijalankan.")
elif failed <= 2:
    print("  ⚠️  Hampir siap! Selesaikan item ❌ di atas.")
else:
    print("  🛑 Beberapa komponen belum siap. Ikuti instruksi di atas.")
print(f"{'='*50}\n")
