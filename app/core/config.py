"""
Application configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")

    # Langflow
    LANGFLOW_API_URL: str = os.getenv(
        "LANGFLOW_API_URL",
        "http://127.0.0.1:7860/api/v1/run/741990f6-cf6e-4039-bcb6-1bf774dd91d7",
    )
    LANGFLOW_API_KEY: str = os.getenv("LANGFLOW_API_KEY", "")

    # Astra DB (for reference / ingest scripts)
    ASTRA_DB_TOKEN: str = os.getenv("ASTRA_DB_TOKEN", "")
    ASTRA_DB_ENDPOINT: str = os.getenv("ASTRA_DB_ENDPOINT", "")
    ASTRA_DB_COLLECTION: str = os.getenv("ASTRA_DB_COLLECTION", "vector_materi_jarkom")

    # Google API Key (Gemini, used by Langflow Agent node)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    # Google Vision / OCR (optional – for handwritten homework grading)
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    USE_GOOGLE_VISION: bool = os.getenv("USE_GOOGLE_VISION", "false").lower() == "true"

    # Tesseract binary path (Windows default; override via TESSERACT_CMD in .env)
    TESSERACT_CMD: str = os.getenv(
        "TESSERACT_CMD",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    )

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
