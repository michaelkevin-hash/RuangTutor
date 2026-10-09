"""
Langflow API client – sends chat messages to the RuangTutor flow.
"""
import uuid
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


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

    logger.info("Calling Langflow: url=%s session=%s msg_preview=%.60s",
                settings.LANGFLOW_API_URL, sid, message)

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                settings.LANGFLOW_API_URL,
                json=payload,
                headers=headers,
            )
            logger.info("Langflow response status: %s", response.status_code)

            if response.status_code != 200:
                logger.error("Langflow error body: %s", response.text[:500])
                response.raise_for_status()

    except httpx.TimeoutException as e:
        logger.error("Langflow TIMEOUT after 90s: %s", e)
        raise
    except httpx.HTTPStatusError as e:
        logger.error("Langflow HTTP %s: %s", e.response.status_code, e.response.text[:300])
        raise
    except httpx.ConnectError as e:
        logger.error("Langflow CONNECT ERROR (is Langflow running on port 7860?): %s", e)
        raise

    data = response.json()
    logger.debug("Langflow raw response keys: %s", list(data.keys()))

    # Navigate the Langflow response envelope:
    # data.outputs[0].outputs[0].results.message.text
    try:
        text = (
            data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        )
        logger.info("Langflow reply (%.80s...)", text)
        return text
    except (KeyError, IndexError, TypeError) as e:
        logger.warning("Could not parse Langflow response structure: %s | raw: %s", e, str(data)[:300])
        # Fallback: return raw JSON so the user always gets something
        return str(data)
