import os
import logging

import httpx

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v25.0"


def _token() -> str:
    return os.environ.get("WHATSAPP_TOKEN", "")


def _messages_url() -> str:
    phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
    return f"{GRAPH_API_BASE}/{phone_id}/messages"


async def send_message(to: str, text: str) -> dict:
    """Send a text message via the WhatsApp Cloud API."""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            _messages_url(),
            headers={
                "Authorization": f"Bearer {_token()}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            },
        )
        res.raise_for_status()
        return res.json()


async def get_media_url(media_id: str) -> tuple[str, str]:
    """Retrieve the download URL and MIME type for a WhatsApp media asset."""
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{GRAPH_API_BASE}/{media_id}",
            headers={"Authorization": f"Bearer {_token()}"},
        )
        res.raise_for_status()
        data = res.json()
        return data["url"], data["mime_type"]


async def download_media(url: str) -> bytes:
    """Download media binary data from a WhatsApp media URL."""
    async with httpx.AsyncClient() as client:
        res = await client.get(
            url,
            headers={"Authorization": f"Bearer {_token()}"},
        )
        res.raise_for_status()
        return res.content


async def mark_as_read(message_id: str) -> None:
    """Send a read receipt and typing indicator for the given message."""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            _messages_url(),
            headers={
                "Authorization": f"Bearer {_token()}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
                "typing_indicator": {"type": "text"},
            },
        )
        if not res.is_success:
            logger.error("Failed to mark message as read: %s", res.text)
