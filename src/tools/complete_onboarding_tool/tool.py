from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import COMPLETE_ONBOARDING_TOOL_DESCRIPTION


@tool(description=COMPLETE_ONBOARDING_TOOL_DESCRIPTION)
def complete_onboarding(
    runtime: ToolRuntime,
) -> Command:
    """Mark the user as onboarded after successful backend registration."""
    return Command(
        update={
            "is_user_onboarded": True,
            "active_skill": "",
            "messages": [
                ToolMessage(
                    content="Onboarding complete. The user now has full access to ADA Finance.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
