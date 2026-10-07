"""
Telegram update handlers.

Supported update types
-----------------------
- /start          → greeting
- /help           → usage instructions
- text message    → routed to Langflow (Tutor mode)
- photo message   → OCR → Langflow (Korektor mode)
"""
import logging
from telegram import Update, PhotoSize
from telegram.ext import ContextTypes

from app.services.langflow_client import ask_langflow
from app.services.ocr_service import extract_text_from_image_url

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Per-user session registry (in-memory; swap for Redis in production)
# --------------------------------------------------------------------------- #
_sessions: dict[int, str] = {}


def _get_session(user_id: int) -> str:
    """Return (and lazily create) a stable session ID for a Telegram user."""
    import uuid

    if user_id not in _sessions:
        _sessions[user_id] = str(uuid.uuid4())
    return _sessions[user_id]


# --------------------------------------------------------------------------- #
#  /start
# --------------------------------------------------------------------------- #
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome = (
        "👋 Halo! Aku *RuangTutor*, Asisten Edukasi AI-mu!\n\n"
        "Aku bisa membantu kamu dengan dua cara:\n"
        "📚 *Mode Tutor* – Tanya materi pelajaran apa saja, aku siap jelaskan!\n"
        "📝 *Mode Korektor* – Kirim foto tugas tulisan tanganmu, aku akan menilai & memberi masukan.\n\n"
        "Ketik /help untuk panduan lengkap."
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


# --------------------------------------------------------------------------- #
#  /help
# --------------------------------------------------------------------------- #
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "*Panduan RuangTutor* 🎓\n\n"
        "*Mode Tutor (Tanya Jawab)*\n"
        "• Ketik pertanyaan pelajaran langsung, contoh:\n"
        "  _\"Apa itu CSMA/CD?\"_\n"
        "  _\"Jelaskan perbedaan TCP dan UDP\"_\n\n"
        "*Mode Korektor (Penilaian Tugas)*\n"
        "• Kirim *foto* tugas tulisan tanganmu.\n"
        "• AI akan membaca tulisanmu, menilai, dan memberi rekomendasi belajar.\n\n"
        "*Tips:* Foto yang terang & tulisan rapi = hasil OCR lebih akurat! 📷"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# --------------------------------------------------------------------------- #
#  Text messages → Tutor mode
# --------------------------------------------------------------------------- #
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    session_id = _get_session(user.id)
    user_text = update.message.text.strip()

    # Show typing indicator
    await update.message.chat.send_action("typing")

    try:
        reply = await ask_langflow(user_text, session_id=session_id)
    except Exception as exc:
        logger.exception("Langflow request failed for user %s", user.id)
        reply = (
            "⚠️ Maaf, ada gangguan koneksi ke server AI. Coba lagi dalam beberapa detik ya!"
        )

    await update.message.reply_text(reply)


# --------------------------------------------------------------------------- #
#  Photo messages → OCR → Korektor mode
# --------------------------------------------------------------------------- #
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    session_id = _get_session(user.id)

    await update.message.reply_text("📷 Foto diterima! Sedang membaca tulisanmu...")
    await update.message.chat.send_action("typing")

    # Pick the highest-resolution photo
    photo: PhotoSize = update.message.photo[-1]

    try:
        # 1. Get download URL from Telegram
        file_obj = await context.bot.get_file(photo.file_id)
        image_url = file_obj.file_path  # full HTTPS URL

        # 2. OCR
        extracted_text = await extract_text_from_image_url(image_url)

        if not extracted_text:
            await update.message.reply_text(
                "😕 Aku tidak berhasil membaca tulisan di foto ini.\n"
                "Pastikan foto cukup terang dan tulisan terlihat jelas, lalu coba kirim ulang."
            )
            return

        # 3. Build a korektor prompt and send to Langflow
        korektor_prompt = (
            f"[MODE KOREKTOR]\n"
            f"Berikut adalah teks hasil OCR dari foto tugas siswa:\n\n"
            f"{extracted_text}\n\n"
            f"Tolong nilai jawaban siswa ini, hitung skornya, identifikasi kesalahan, "
            f"dan berikan rekomendasi belajar."
        )
        reply = await ask_langflow(korektor_prompt, session_id=session_id)

    except Exception as exc:
        logger.exception("Photo handler failed for user %s", user.id)
        reply = (
            "⚠️ Terjadi kesalahan saat memproses fotomu. "
            "Pastikan gambar jelas dan coba lagi ya!"
        )

    await update.message.reply_text(reply)
