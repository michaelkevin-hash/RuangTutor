"""
Langflow API client – sends chat messages to the RuangTutor flow.
"""
import uuid
import httpx
from app.core.config import settings


async def ask_langflow(message: str, session_id: str | None = None) -> str:
    """
    Send *message* to the Langflow flow and return the AI text response.

    Parameters
    ----------
    message:    The user's input text (question or OCR-extracted homework).
    session_id: Optional session ID for per-user conversation history.
                A new UUID is generated if not supplied.
    """
    sid = session_id or str(uuid.uuid4())

    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": message,
        "session_id": sid,
    }
    headers = {}
    if settings.LANGFLOW_API_KEY:
        headers["x-api-key"] = settings.LANGFLOW_API_KEY

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            settings.LANGFLOW_API_URL,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()

    data = response.json()

    # Navigate the Langflow response envelope:
    # data.outputs[0].outputs[0].results.message.text
    try:
        text = (
            data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        )
    except (KeyError, IndexError, TypeError):
        # Fallback: return raw JSON so the user always gets something
        text = str(data)

    return text
