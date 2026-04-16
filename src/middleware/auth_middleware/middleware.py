"""Auth middleware — seeds tokens and workspace_id from run context into state.

The frontend proxy injects access_token, refresh_token, and workspace_id into
the run context. This middleware copies them into state on the first turn so
that the api_request tool can read and update them.

If workspace_id is not provided in context, the middleware resolves it
automatically by calling GET /v1/workspaces/default.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from langchain.agents.middleware.types import AgentMiddleware, hook_config
from langgraph.runtime import Runtime

from src.middleware.auth_middleware.state import AuthState

logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


async def _resolve_default_workspace(access_token: str) -> str:
    """Fetch the user's default workspace ID from the backend."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{API_BASE_URL}/v1/workspaces/default",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                body = response.json()
                workspace_id = body.get("data", {}).get("id", "")
                if workspace_id:
                    return str(workspace_id)
    except Exception as exc:
        logger.warning("Failed to resolve default workspace: %s", exc)
    return ""


class AuthMiddleware(AgentMiddleware[AuthState]):
    """Seeds auth tokens and workspace_id from run context into state.

    Reads access_token, refresh_token, and workspace_id from the run context
    (injected by the frontend proxy) and syncs them into state. If
    workspace_id is not provided, resolves it via the backend.

    This sync runs on every turn so the thread state can pick up newer
    cookies or refreshed tokens from the frontend proxy instead of getting
    stuck with stale credentials from an older turn.
    """

    state_schema = AuthState

    @hook_config(can_jump_to=["end"])
    async def abefore_agent(
        self, state: AuthState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Sync tokens and workspace_id from context into state."""

        # Read from run context
        context = getattr(runtime, "context", None)
        access_token = getattr(context, "access_token", "") if context else ""
        refresh_token = getattr(context, "refresh_token", "") if context else ""
        workspace_id = getattr(context, "workspace_id", "") if context else ""
        state_access_token = state.get("access_token", "")
        state_refresh_token = state.get("refresh_token", "")
        state_workspace_id = state.get("workspace_id", "")

        # Fall back to state if the current turn context omitted a token.
        if not access_token:
            access_token = state_access_token
        if not refresh_token:
            refresh_token = state_refresh_token
        if not workspace_id:
            workspace_id = state_workspace_id

        if not access_token:
            logger.warning("No access_token available in run context or state.")
            return None

        # Resolve workspace_id if not provided
        if not workspace_id:
            logger.info("No workspace_id in context, resolving default workspace...")
            workspace_id = await _resolve_default_workspace(access_token)
            if workspace_id:
                logger.info("Resolved default workspace: %s", workspace_id)
            else:
                logger.warning("Could not resolve default workspace.")

        updates: dict[str, Any] = {}

        if access_token and access_token != state_access_token:
            updates["access_token"] = access_token
        if refresh_token and refresh_token != state_refresh_token:
            updates["refresh_token"] = refresh_token
        if workspace_id and workspace_id != state_workspace_id:
            updates["workspace_id"] = workspace_id

        if updates:
            logger.info("Auth tokens and workspace_id synced into state.")
            return updates

        return None
