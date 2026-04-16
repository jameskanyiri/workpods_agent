from typing import Literal

from pydantic import BaseModel, Field


SupportedLLM = Literal[
    "openai:gpt-5.2",
    "openai:gpt-5.4",
    "anthropic:claude-opus-4-6",
    "anthropic:claude-sonnet-4-6",
    "anthropic:claude-haiku-4-5-20251001",
]


class AgentContext(BaseModel):

    user_name: str = Field(
        default="No user name",
        description="The name of the user",
    )

    preferred_llm: SupportedLLM = Field(
        default="openai:gpt-5.4",
        description="The preferred LLM to use for the agent (all models support tool calling)",
    )

    access_token: str = Field(
        default="",
        description="JWT access token for the Workpods backend API",
    )

    refresh_token: str = Field(
        default="",
        description="JWT refresh token for obtaining new access tokens",
    )

    workspace_id: str = Field(
        default="",
        description="Current workspace UUID. If empty, the agent will resolve it via GET /v1/workspaces/default.",
    )

