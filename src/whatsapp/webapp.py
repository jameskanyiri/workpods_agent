import os
import logging

from starlette.applications import Starlette
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


async def handle_incoming_message(request: Request):
    """Meta sends incoming WhatsApp messages to this endpoint."""
    body = await request.json()

    entry = (body.get("entry") or [None])[0]
    change = ((entry or {}).get("changes") or [None])[0] if entry else None
    message = ((change or {}).get("value", {}).get("messages") or [None])[0] if change else None

    if not message:
        return JSONResponse({"status": "no message"}, status_code=200)

    sender = message.get("from")
    text = (message.get("text") or {}).get("body")
    message_id = message.get("id")

    if not text:
        return JSONResponse({"status": "no text"}, status_code=200)

    logger.info("Message from %s: %s", sender, text)

    try:
        if message_id:
            await mark_as_read(message_id)

        ai_response = await get_agent_response(sender, text)
        logger.info("AI Response: %s", ai_response)

        if ai_response:
            await send_message(sender, ai_response)
    except Exception:
        logger.exception("Error processing message")

    # Always return 200 so WhatsApp doesn't retry
    return JSONResponse({"status": "ok"}, status_code=200)


app = Starlette(
    routes=[
        Route("/webhook", verify_webhook, methods=["GET"]),
        Route("/webhook", handle_incoming_message, methods=["POST"]),
    ]
)
