from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import THINK_TOOL_DESCRIPTION


@tool(description=THINK_TOOL_DESCRIPTION)
def think_tool(
    reflection: str,
    runtime: ToolRuntime,
) -> Command:
    """
    Reflect on what has been done (or what the user requested) and plan what to do next.
    Returns a message in the format: what's done/requested, then what to do next.
    """

    return Command(
        update={
            "messages": [
                ToolMessage(content=reflection, tool_call_id=runtime.tool_call_id)
            ]
        }
    )
