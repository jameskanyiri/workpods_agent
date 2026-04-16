from langchain.agents import AgentState
from typing import NotRequired


class PreCompletionCheckState(AgentState):
    """State extension for pre-completion verification tracking."""

    _completion_check_count: NotRequired[int]
    """Number of verification passes completed. Private — not exposed to the agent."""
