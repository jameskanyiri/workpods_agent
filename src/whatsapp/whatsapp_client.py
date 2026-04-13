import os
import logging

import httpx

logger = logging.getLogger(__name__)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_API_URL = f"https://graph.facebook.com/v25.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


async def send_message(to: str, text: str) -> dict:
    """Send a text message via the WhatsApp Cloud API."""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            WHATSAPP_API_URL,
            headers={
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
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


async def mark_as_read(message_id: str) -> None:
    """Send a read receipt and typing indicator for the given message."""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            WHATSAPP_API_URL,
            headers={
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
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
