"""
OCR service – extract text from an image (handwritten homework photo).

Supports two backends:
  1. Google Cloud Vision API  (USE_GOOGLE_VISION=true)
  2. Tesseract OCR             (default, no cloud credentials needed)

Install notes:
  pip install google-cloud-vision  # for backend 1
  pip install pytesseract Pillow   # for backend 2 (also install tesseract binary)
"""
import io
import httpx
from app.core.config import settings

# Configure Tesseract binary path from settings (Windows needs explicit path)
try:
    import pytesseract as _pt
    _pt.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
except ImportError:
    pass


async def extract_text_from_image_url(image_url: str) -> str:
    """Download a Telegram file URL and run OCR on it."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(image_url)
        resp.raise_for_status()
        image_bytes = resp.content

    return extract_text_from_bytes(image_bytes)


def extract_text_from_bytes(image_bytes: bytes) -> str:
    """Run OCR on raw image bytes and return the extracted text."""
    if settings.USE_GOOGLE_VISION:
        return _google_vision_ocr(image_bytes)
    return _tesseract_ocr(image_bytes)


def _tesseract_ocr(image_bytes: bytes) -> str:
    """Use pytesseract (local) – supports Indonesian + English."""
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes))
        # Try Indonesian first, fallback to English
        text = pytesseract.image_to_string(image, lang="ind+eng")
        return text.strip()
    except ImportError as exc:
        raise RuntimeError(
            "pytesseract / Pillow not installed. "
            "Run: pip install pytesseract Pillow"
        ) from exc


def _google_vision_ocr(image_bytes: bytes) -> str:
    """Use Google Cloud Vision Document Text Detection."""
    try:
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.document_text_detection(image=image)
        if response.error.message:
            raise RuntimeError(f"Google Vision error: {response.error.message}")
        return response.full_text_annotation.text.strip()
    except ImportError as exc:
        raise RuntimeError(
            "google-cloud-vision not installed. "
            "Run: pip install google-cloud-vision"
        ) from exc
