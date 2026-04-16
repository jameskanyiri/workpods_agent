from langchain.agents import AgentState
from typing import NotRequired


class LoopDetectionState(AgentState):
    """State extension for tracking repeated tool call patterns."""

    _tool_call_counts: NotRequired[dict[str, int]]
    """Counts of tool calls keyed by a signature (e.g. 'edit_file:/path/to/file').
    Private — not exposed to the agent."""

    _loop_warnings: NotRequired[list[str]]
    """Pending warnings to inject into the next model call.
    Private — not exposed to the agent."""
