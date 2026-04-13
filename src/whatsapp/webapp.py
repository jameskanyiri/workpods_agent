import os
import logging

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.routing import Route

from src.whatsapp.whatsapp_client import send_message, mark_as_read
from src.whatsapp.agent_client import get_agent_response

logger = logging.getLogger(__name__)

WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")


async def verify_webhook(request: Request):
    """Meta calls this endpoint to verify the webhook during setup."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified")
        return PlainTextResponse(challenge, status_code=200)

    return PlainTextResponse("Forbidden", status_code=403)


def _build_media_prompt(msg_type: str, message: dict) -> str | None:
    """Build a text prompt describing an incoming media message."""
    media_info = message.get(msg_type, {})
    media_id = media_info.get("id")
    if not media_id:
        return None

    mime_type = media_info.get("mime_type", "unknown")
    caption = media_info.get("caption", "")
    caption_part = f" Caption: {caption}." if caption else ""

    if msg_type == "image":
        return (
            f"User sent an image [media_id: {media_id}, mime_type: {mime_type}].{caption_part} "
            "Use the process_media tool to retrieve and analyze it."
        )
    if msg_type == "document":
        filename = media_info.get("filename", "unknown")
        return (
            f"User sent a document '{filename}' [media_id: {media_id}, mime_type: {mime_type}].{caption_part} "
            "Use the process_media tool to retrieve and process it."
        )
    if msg_type == "audio":
        return (
            f"User sent an audio message [media_id: {media_id}, mime_type: {mime_type}]. "
            "Use the process_media tool to retrieve it."
        )
    return None


async def handle_incoming_message(request: Request):
    """Meta sends incoming WhatsApp messages to this endpoint."""
    body = await request.json()

    entry = (body.get("entry") or [None])[0]
    change = ((entry or {}).get("changes") or [None])[0] if entry else None
    message = ((change or {}).get("value", {}).get("messages") or [None])[0] if change else None

    if not message:
        return JSONResponse({"status": "no message"}, status_code=200)

    # Extract contact profile name from the webhook payload
    contacts = (change or {}).get("value", {}).get("contacts") or []
    sender_name = contacts[0].get("profile", {}).get("name") if contacts else None

    sender = message.get("from")
    message_id = message.get("id")
    msg_type = message.get("type")

    # Build the text to send to the agent based on message type
    if msg_type == "text":
        agent_input = (message.get("text") or {}).get("body")
    elif msg_type in ("image", "document", "audio"):
        agent_input = _build_media_prompt(msg_type, message)
    else:
        return JSONResponse({"status": "unsupported message type"}, status_code=200)

    if not agent_input:
        return JSONResponse({"status": "no content"}, status_code=200)

    logger.info("Message from %s (%s): %s", sender, msg_type, agent_input)

    # Return 200 immediately so WhatsApp doesn't retry, process in background
    task = BackgroundTask(_process_message, sender, agent_input, message_id, sender_name)
    return JSONResponse({"status": "ok"}, status_code=200, background=task)


async def _process_message(
    sender: str, agent_input: str, message_id: str | None, sender_name: str | None
):
    """Process a message in the background after returning 200 to WhatsApp."""
    try:
        if message_id:
            await mark_as_read(message_id)

        ai_response = await get_agent_response(sender, agent_input, sender_name or "")
        logger.info("AI Response: %s", ai_response)

        if ai_response:
            await send_message(sender, ai_response)
    except Exception:
        logger.exception("Error processing message")


app = Starlette(
    routes=[
        Route("/webhook", verify_webhook, methods=["GET"]),
        Route("/webhook", handle_incoming_message, methods=["POST"]),
    ]
)
