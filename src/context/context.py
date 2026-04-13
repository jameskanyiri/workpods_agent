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

    user_id: str = Field(
        default="50f1f0a7-24a0-4276-8075-fdd3158b102e",
        description="User ID"
    )
    user_name: str = Field(
        default="James Kanyiri",
        description="The name of the user",
    )

    preferred_llm: SupportedLLM = Field(
        default="openai:gpt-5.4",
        description="The preferred LLM to use for the agent (all models support tool calling)",
    )

    company_name: str = Field(
        default="",
        description="The business/company name for the current organisation",
    )
    kra_pin: str = Field(
        default="",
        description="KRA PIN of the organisation (validated against iTax)",
    )
    fiscal_year_end: str = Field(
        default="December",
        description="Fiscal year end month (e.g., December, June)",
    )
    vat_registered: bool = Field(
        default=False,
        description="Whether the organisation is VAT-registered with KRA",
    )
   
