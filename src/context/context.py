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

