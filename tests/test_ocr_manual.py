"""
Test OCR service – baca teks dari file gambar lokal.

Jalankan:
    python tests/test_ocr_manual.py path/ke/gambar.jpg
    python tests/test_ocr_manual.py   (pakai gambar contoh built-in)
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


def test_with_sample_image():
    """Generate a sample handwritten-style image using Pillow and run OCR."""
    from PIL import Image, ImageDraw, ImageFont
    import io

    # Buat gambar contoh dengan teks simulasi jawaban siswa
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    sample_text = [
        "Nama: Budi Santoso",
        "Kelas: XI TKJ",
        "",
        "1. CSMA/CD = Carrier Sense Multiple Access",
        "   with Collision Detection",
        "2. Digunakan pada Ethernet tradisional",
        "3. Cara kerja: dengarkan kabel dulu",
        "   sebelum kirim data",
    ]

    y = 20
    for line in sample_text:
        draw.text((20, y), line, fill=(0, 0, 0))
        y += 30

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes.read()


async def main():
    from app.services.ocr_service import extract_text_from_bytes

    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
        if not image_path.exists():
            print(f"❌ File tidak ditemukan: {image_path}")
            sys.exit(1)
        print(f"📷 Membaca file: {image_path}")
        image_bytes = image_path.read_bytes()
    else:
        print("📷 Tidak ada file diberikan – menggunakan gambar contoh sintetis...")
        image_bytes = test_with_sample_image()

    print("⏳ Menjalankan OCR...\n")

    try:
        text = extract_text_from_bytes(image_bytes)
        if text:
            print("📝 Teks hasil OCR:")
            print("─" * 60)
            print(text)
            print("─" * 60)
            print("\n✅ OCR berhasil!\n")
        else:
            print("⚠️  OCR berjalan tapi tidak menemukan teks.")
            print("Coba dengan foto yang lebih terang dan tulisan lebih jelas.\n")
    except RuntimeError as e:
        print(f"\n❌ OCR Error: {e}\n")
        print("Cara install Tesseract di Windows:")
        print("  1. Download: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  2. Saat install, centang 'Indonesian' di Additional Language Data")
        print("  3. Restart terminal setelah install\n")


asyncio.run(main())
