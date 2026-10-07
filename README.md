# RuangTutor 🎓

> **AI Education Assistant untuk siswa Indonesia**  
> Chatbot Telegram berbasis LLM yang berfungsi sebagai **Tutor Pribadi** sekaligus **Korektor Tugas Otomatis**.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@RuangTutor__bot-blue.svg)](https://t.me/RuangTutor_bot)

---

## ✨ Fitur

| Fitur | Deskripsi |
|---|---|
| 📚 **Mode Tutor** | Siswa kirim pertanyaan pelajaran → AI jelaskan konsep, berikan contoh, dan pancing pemahaman |
| 📝 **Mode Korektor** | Siswa kirim foto tugas tulisan tangan → OCR otomatis → AI nilai & beri rekomendasi belajar |
| 🧠 **RAG (Retrieval-Augmented Generation)** | Jawaban berbasis dokumen materi yang sudah diindeks di Astra DB Vector Store |
| 💬 **Memori Percakapan** | Setiap pengguna punya sesi percakapan terpisah |

---

## 🏗️ Arsitektur

```
Telegram User
     │
     ▼
Telegram Servers  ──POST──►  FastAPI /webhook  (main.py)
                                    │
                         python-telegram-bot (PTB)
                          ┌─────────┴──────────┐
                    text_handler          photo_handler
                          │                    │
                   Langflow API         OCR Service
                  (LLM + AstraDB)     (Tesseract / Google Vision)
                          │                    │
                          └──────────┬─────────┘
                                Langflow API
                            (RuangTutor Flow)
                                     │
                               Gemini Flash + AstraDB
                               (vector_materi_jarkom)
```

---

## 🚀 Quick Start

### 1. Clone repo

```bash
git clone https://github.com/YOUR_USERNAME/RuangTutor.git
cd RuangTutor
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# For local Tesseract OCR (required unless using Google Vision)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-ind
# macOS:
brew install tesseract tesseract-lang
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env – fill in your tokens and URLs
```

Key variables:

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) |
| `WEBHOOK_URL` | Your public HTTPS domain (e.g. ngrok URL for local dev) |
| `LANGFLOW_API_URL` | Langflow flow run endpoint |
| `LANGFLOW_API_KEY` | Langflow API key (leave blank if not set) |
| `USE_GOOGLE_VISION` | `true` to use Google Cloud Vision OCR |

### 4. Run Langflow locally

```bash
pip install langflow
langflow run
# Then import the RuangTutor flow JSON from /langflow/RuangTutor_flow.json
```

### 5. Expose local server (development)

```bash
# In one terminal:
uvicorn main:app --reload --port 8000

# In another terminal (ngrok):
ngrok http 8000
# Copy the HTTPS URL → set as WEBHOOK_URL in .env, then restart uvicorn
```

### 6. Run in production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📁 Project Structure

```
RuangTutor/
├── main.py                        # FastAPI app + webhook endpoint
├── requirements.txt
├── .env.example
├── gitignore.txt                  # Rename to .gitignore
└── app/
    ├── core/
    │   └── config.py              # Settings from .env
    ├── services/
    │   ├── langflow_client.py     # HTTP client for Langflow API
    │   └── ocr_service.py         # OCR (Tesseract / Google Vision)
    └── handlers/
        └── telegram_handlers.py   # /start, /help, text, photo handlers
```

---

## 🤖 Telegram Bot

Live bot: [@RuangTutor_bot](https://t.me/RuangTutor_bot)

### Commands

| Command | Action |
|---|---|
| `/start` | Greeting + mode overview |
| `/help` | Detailed usage guide |
| Any text | Tutor mode – AI explains the topic |
| Send a photo | Korektor mode – OCR + grading |

---

## 📚 Langflow Flow Details

The AI pipeline (built in IBM Skills Build / Langflow) consists of:

1. **Prompt Template** – Loads Computer Networks subject material (Ethernet, IEEE 802.11)  
2. **Split Text** – Chunks the material (size 1000, overlap 200)  
3. **Astra DB** (vector_materi_jarkom) – NVIDIA-embedded vector store for semantic search  
4. **Agent** (Gemini Flash) – RAG agent with `search_documents` tool  
5. **Chat I/O** – Telegram-connected input/output

---

## 🛣️ Roadmap

- [x] Langflow RAG flow (Astra DB + Gemini)
- [x] FastAPI webhook backend
- [x] Telegram text handler (Tutor mode)
- [x] Telegram photo handler + OCR (Korektor mode)
- [ ] Redis-backed session store for scalability
- [ ] Teacher dashboard (score aggregation)
- [ ] Multi-subject support (beyond Computer Networks)
- [ ] WhatsApp integration via WhatsApp Business API

---

## 📄 License

MIT © 2026 RuangTutor Team
