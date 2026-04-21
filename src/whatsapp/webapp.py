import os
import base64
import logging

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.routing import Route

from src.whatsapp.whatsapp_client import (
    send_message,
    mark_as_read,
    get_media_url,
    download_media,
)
from src.whatsapp.agent_client import get_agent_response

logger = logging.getLogger(__name__)

WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")

# WhatsApp allows up to ~100MB, but OpenAI's vision inputs and LangGraph
# JSON payload limits make 20MB a safer cap. Larger media falls back to a
# text prompt so the run still completes.
MAX_DIRECT_MEDIA_BYTES = 20 * 1024 * 1024


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


def _build_media_fallback_prompt(msg_type: str, message: dict) -> str | None:
    """Text fallback when the media can't be embedded directly."""
    media_info = message.get(msg_type, {})
    media_id = media_info.get("id")
    if not media_id:
        return None

    mime_type = media_info.get("mime_type", "unknown")
    caption = media_info.get("caption", "")
    caption_part = f" Caption: {caption}." if caption else ""

    if msg_type == "image":
        return (
            f"User sent an image but it could not be attached "
            f"[mime_type: {mime_type}].{caption_part} "
            "Ask them to resend or describe what they need help with."
        )
    if msg_type == "document":
        filename = media_info.get("filename", "unknown")
        return (
            f"User sent a document '{filename}' but it could not be attached "
            f"[mime_type: {mime_type}].{caption_part} "
            "Ask them to resend or describe what they need help with."
        )
    if msg_type == "audio":
        return (
            f"User sent an audio message [mime_type: {mime_type}]. "
            "Audio is not supported yet — ask them to send a text message."
        )
    return None


async def _download_and_encode_media(media_id: str) -> tuple[str, str] | None:
    """Download WhatsApp media and return (base64_string, mime_type), or None."""
    try:
        url, mime_type = await get_media_url(media_id)
        media_bytes = await download_media(url)
        if len(media_bytes) > MAX_DIRECT_MEDIA_BYTES:
            logger.warning(
                "Media %s too large (%d bytes), falling back to text",
                media_id,
                len(media_bytes),
            )
            return None
        b64_data = base64.b64encode(media_bytes).decode("utf-8")
        return b64_data, mime_type
    except Exception:
        logger.exception("Failed to download media %s", media_id)
        return None


def _build_media_content_blocks(
    b64_data: str, mime_type: str, caption: str, filename: str
) -> list[dict]:
    """Build LangChain-standard multimodal content blocks for a HumanMessage.

    Uses `source_type: "base64"` which LangChain translates to the right
    provider-native shape (OpenAI image_url / Anthropic source / etc.).
    """
    text = caption or "The user sent this file. Analyze it and respond helpfully."

    if mime_type.startswith("image/"):
        return [
            {"type": "text", "text": text},
            {
                "type": "image",
                "source_type": "base64",
                "data": b64_data,
                "mime_type": mime_type,
            },
        ]

    # PDFs, spreadsheets, and other documents go through the "file" block.
    return [
        {"type": "text", "text": text},
        {
            "type": "file",
            "source_type": "base64",
            "data": b64_data,
            "mime_type": mime_type,
            "filename": filename,
        },
    ]


async def _resolve_media_input(
    msg_type: str, message: dict
) -> str | list[dict] | None:
    """Resolve an incoming media message to either multimodal blocks or a text fallback."""
    # Audio isn't multimodal-native for the default (OpenAI chat) model —
    # send a text prompt asking the user to resend.
    if msg_type == "audio":
        return _build_media_fallback_prompt(msg_type, message)

    media_info = message.get(msg_type, {})
    media_id = media_info.get("id")
    if not media_id:
        return _build_media_fallback_prompt(msg_type, message)

    result = await _download_and_encode_media(media_id)
    if result is None:
        return _build_media_fallback_prompt(msg_type, message)

    b64_data, mime_type = result
    caption = media_info.get("caption", "")
    filename = media_info.get("filename", "document")
    return _build_media_content_blocks(b64_data, mime_type, caption, filename)


async def handle_incoming_message(request: Request):
    """Meta sends incoming WhatsApp messages to this endpoint."""
    body = await request.json()

    entry = (body.get("entry") or [None])[0]
    change = ((entry or {}).get("changes") or [None])[0] if entry else None
    message = ((change or {}).get("value", {}).get("messages") or [None])[0] if change else None

    if not message:
        return JSONResponse({"status": "no message"}, status_code=200)

    contacts = (change or {}).get("value", {}).get("contacts") or []
    sender_name = contacts[0].get("profile", {}).get("name") if contacts else None

    sender = message.get("from")
    message_id = message.get("id")
    msg_type = message.get("type")

    if msg_type == "text":
        agent_input: str | list[dict] | None = (message.get("text") or {}).get("body")
    elif msg_type in ("image", "document", "audio"):
        agent_input = await _resolve_media_input(msg_type, message)
    else:
        return JSONResponse({"status": "unsupported message type"}, status_code=200)

    if not agent_input:
        return JSONResponse({"status": "no content"}, status_code=200)

    if isinstance(agent_input, list):
        logger.info(
            "Message from %s (%s): [multimodal: %d blocks]",
            sender,
            msg_type,
            len(agent_input),
        )
    else:
        logger.info("Message from %s (%s): %s", sender, msg_type, agent_input)

    # Return 200 immediately so WhatsApp doesn't retry; process in background.
    task = BackgroundTask(_process_message, sender, agent_input, message_id, sender_name)
    return JSONResponse({"status": "ok"}, status_code=200, background=task)


async def _process_message(
    sender: str,
    agent_input: str | list[dict],
    message_id: str | None,
    sender_name: str | None,
):
    """Process a message in the background after returning 200 to WhatsApp."""
    import asyncio

    async def _keep_typing(mid: str, cancel_event: asyncio.Event):
        """Re-send the typing indicator every 20s until cancelled."""
        while not cancel_event.is_set():
            try:
                await asyncio.wait_for(cancel_event.wait(), timeout=20)
                break
            except asyncio.TimeoutError:
                pass
            try:
                await mark_as_read(mid)
            except Exception:
                logger.warning("Failed to refresh typing indicator")

    try:
        if message_id:
            await mark_as_read(message_id)

        cancel_typing = asyncio.Event()
        typing_task = (
            asyncio.create_task(_keep_typing(message_id, cancel_typing))
            if message_id
            else None
        )

        try:
            ai_response = await get_agent_response(
                sender, agent_input, sender_name or ""
            )
        finally:
            cancel_typing.set()
            if typing_task:
                typing_task.cancel()

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
