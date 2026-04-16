from langchain.agents.middleware.types import AgentState
from typing import NotRequired


class AuthState(AgentState):
    """State extension carrying auth tokens and workspace context."""

    access_token: NotRequired[str]
    """JWT access token for the Workpods backend API."""

    refresh_token: NotRequired[str]
    """JWT refresh token for obtaining new access tokens."""

    workspace_id: NotRequired[str]
    """Current workspace UUID for API calls."""
