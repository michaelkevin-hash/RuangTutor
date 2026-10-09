"""
RuangTutor – FastAPI entry point.

Architecture
------------
  Telegram  ──►  POST /webhook  ──►  python-telegram-bot PTB
                                          │
                               ┌──────────┴──────────┐
                               │                     │
                         text_handler          photo_handler
                               │                     │
                         Langflow API          OCR → Langflow API
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from telegram import Update, Bot
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

from app.core.config import settings
from app.handlers.telegram_handlers import (
    start_handler,
    help_handler,
    text_handler,
    photo_handler,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Build the PTB application (does NOT start polling – we use webhooks)
# --------------------------------------------------------------------------- #
ptb_app: Application | None = None


def _build_ptb_app() -> Application:
    # Increase timeouts — default 5s often fails on Indonesian networks
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )
    app = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .request(request)
        .updater(None)          # disable built-in polling; webhook only
        .build()
    )
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
    )
    return app


# --------------------------------------------------------------------------- #
#  Lifespan: register webhook on startup, remove on shutdown
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    global ptb_app

    ptb_app = _build_ptb_app()
    await ptb_app.initialize()

    if settings.WEBHOOK_URL:
        webhook_endpoint = f"{settings.WEBHOOK_URL.rstrip('/')}/webhook"
        await ptb_app.bot.set_webhook(url=webhook_endpoint)
        logger.info("Webhook set to %s", webhook_endpoint)
    else:
        logger.warning(
            "WEBHOOK_URL not configured – Telegram will not deliver updates. "
            "Set WEBHOOK_URL in your .env file."
        )

    yield  # ← application runs here

    logger.info("Shutting down – removing webhook …")
    if settings.WEBHOOK_URL:
        await ptb_app.bot.delete_webhook()
    await ptb_app.shutdown()


# --------------------------------------------------------------------------- #
#  FastAPI app
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="RuangTutor Bot",
    description="AI Education Assistant for Indonesian students – Telegram webhook backend",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "RuangTutor Bot"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}


@app.post("/webhook", tags=["telegram"])
async def telegram_webhook(request: Request):
    """Receive Telegram update and dispatch to PTB handlers."""
    if ptb_app is None:
        return Response(status_code=503, content="Bot not initialised")

    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return Response(status_code=200)
