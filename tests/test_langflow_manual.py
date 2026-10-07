"""
Test manual untuk Langflow API – kirim pesan nyata dan lihat respons.

Jalankan:
    python tests/test_langflow_manual.py "Apa itu CSMA/CD?"
    python tests/test_langflow_manual.py   (pakai pertanyaan default)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


async def main():
    from app.services.langflow_client import ask_langflow

    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Apa perbedaan CSMA/CD dan CSMA/CA?"

    print(f"\n📤 Pertanyaan  : {question}")
    print("⏳ Menunggu respons Langflow...\n")

    try:
        answer = await ask_langflow(question, session_id="test-session-001")
        print("📥 Jawaban AI :")
        print("─" * 60)
        print(answer)
        print("─" * 60)
        print("\n✅ Langflow OK!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Pastikan Langflow sudah berjalan: langflow run\n")


asyncio.run(main())
