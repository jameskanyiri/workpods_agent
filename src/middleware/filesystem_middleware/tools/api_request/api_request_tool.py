import asyncio
import json
import logging
import os
import httpx
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Any

from src.middleware.filesystem_middleware.tools.api_request.description import API_REQUEST_TOOL_DESCRIPTION
from src.middleware.filesystem_middleware.state import FilesystemState
from src.middleware.filesystem_middleware.prompt import TOO_LARGE_TOOL_MSG
from src.middleware.filesystem_middleware.utils import create_content_preview
from src.middleware.filesystem_middleware.config import NUM_CHARS_PER_TOKEN

logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Responses larger than this (in estimated tokens) get offloaded to the VFS
_OFFLOAD_TOKEN_THRESHOLD = 2000

# In-flight refresh cache to avoid race conditions when multiple parallel
# api_request calls all hit 401 at the same time.  The first call performs
# the refresh and caches the result; subsequent calls reuse it.
_inflight_refresh: dict[str, "asyncio.Task[dict | None]"] = {}


async def _do_refresh(refresh_token: str) -> dict | None:
    """Call the Workpods backend refresh endpoint to get new tokens."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{API_BASE_URL}/v1/auth/refresh",
                json={"refresh_token": refresh_token},
            )
            if response.status_code == 200:
                body = response.json()
                tokens = body.get("tokens", body)
                access = tokens.get("access_token")
                refresh = tokens.get("refresh_token", refresh_token)
                if access:
                    logger.info("[api_request] Token refresh succeeded.")
                    return {"access_token": access, "refresh_token": refresh}
            logger.warning(
                "[api_request] Token refresh failed: status=%s body=%s",
                response.status_code,
                response.text[:200],
            )
    except Exception as exc:
        logger.warning("[api_request] Token refresh error: %s", exc)
    return None


async def _refresh_access_token(refresh_token: str) -> dict | None:
    """Deduplicated refresh: if another call is already refreshing with the
    same token, wait for its result instead of making a duplicate request
    (which would fail due to token rotation)."""
    if refresh_token in _inflight_refresh:
        return await _inflight_refresh[refresh_token]

    task = asyncio.ensure_future(_do_refresh(refresh_token))
    _inflight_refresh[refresh_token] = task
    try:
        return await task
    finally:
        _inflight_refresh.pop(refresh_token, None)


async def _make_request(
    method: str,
    endpoint: str,
    access_token: str,
    payload: dict | None = None,
    params: dict | None = None,
) -> tuple[int, Any]:
    """Make an HTTP request and return (status_code, body)."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    url = f"{API_BASE_URL}{endpoint}" if endpoint.startswith("/") else f"{API_BASE_URL}/{endpoint}"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=payload,
                params=params,
            )
            status_code = response.status_code
            try:
                body = response.json()
            except Exception:
                body = response.text
            return status_code, body
        except httpx.RequestError as exc:
            return 0, {"error": True, "detail": str(exc)}


@tool(description=API_REQUEST_TOOL_DESCRIPTION)
async def api_request(
    display_name: str = "Working",
    method: str = "GET",
    endpoint: str = "/",
    payload: dict | None = None,
    params: dict | None = None,
    runtime: ToolRuntime[None, FilesystemState] = None,
) -> Command[Any]:
    """Make an API request to the Workpods backend."""

    # Read tokens from state (seeded by AuthMiddleware)
    access_token = runtime.state.get("access_token", "")
    refresh_token = runtime.state.get("refresh_token", "")

    if not access_token:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="[api_request] No access token available. "
                        "The user may need to log in.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    # First attempt
    status_code, body = await _make_request(method, endpoint, access_token, payload, params)

    state_updates: dict[str, Any] = {}

    # If 401 and we have a refresh token, refresh and retry
    if status_code == 401 and refresh_token:
        logger.info("[api_request] Got 401, attempting token refresh...")
        new_tokens = await _refresh_access_token(refresh_token)
        if new_tokens:
            state_updates["access_token"] = new_tokens["access_token"]
            state_updates["refresh_token"] = new_tokens["refresh_token"]
            status_code, body = await _make_request(
                method, endpoint, new_tokens["access_token"], payload, params
            )
        else:
            logger.warning("[api_request] Token refresh failed, returning auth error.")
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="[api_request] Authentication expired and token refresh failed. "
                            "The user may need to log in again.",
                            tool_call_id=runtime.tool_call_id,
                            status="error",
                        )
                    ],
                }
            )
    elif status_code == 401 and not refresh_token:
        logger.warning("[api_request] Got 401 but no refresh token in state.")
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="[api_request] Authentication expired and no refresh token available. "
                        "The user needs to log in again.",
                        tool_call_id=runtime.tool_call_id,
                        status="error",
                    )
                ],
            }
        )

    # Format response
    if status_code >= 400:
        error_body = {
            "error": True,
            "status_code": status_code,
            "detail": body if isinstance(body, str) else json.dumps(body),
        }
        content = json.dumps(error_body)
    else:
        content = json.dumps(body) if isinstance(body, (dict, list)) else str(body)

    # Offload large responses to VFS so they don't bloat the context window
    char_threshold = NUM_CHARS_PER_TOKEN * _OFFLOAD_TOKEN_THRESHOLD
    if len(content) > char_threshold:
        file_path = f"/large_tool_results/{runtime.tool_call_id}"
        content_sample = create_content_preview(content)
        summary = TOO_LARGE_TOOL_MSG.format(
            tool_call_id=runtime.tool_call_id,
            file_path=file_path,
            content_sample=content_sample,
        )
        logger.info(
            "[api_request] Response too large (%d chars), offloading to %s",
            len(content),
            file_path,
        )
        return Command(
            update={
                **state_updates,
                "files": {
                    file_path: {
                        "content": content,
                        "encoding": "utf-8",
                    }
                },
                "messages": [
                    ToolMessage(
                        content=f"[api_request] {method} {endpoint}\n{summary}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    return Command(
        update={
            **state_updates,
            "messages": [
                ToolMessage(
                    content=f"[api_request] {method} {endpoint}\n{content}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
