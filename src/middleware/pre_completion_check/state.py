from langchain.agents import AgentState
from typing import NotRequired


class PreCompletionCheckState(AgentState):
    """State extension for pre-completion verification tracking."""

    _completion_check_count: NotRequired[int]
    """Number of verification passes completed. Private — not exposed to the agent."""

    _needs_verification: NotRequired[bool]
    """True when a verification pass has just been scheduled. Read by
    awrap_model_call to inject the verification prompt for one model call,
    and cleared by the next aafter_model after the revised response lands."""

    _completion_message_id: NotRequired[str]
    """ID of the AI message that tried to finish and triggered verification.
    Removed from state after the revised response lands so the premature
    'I'm done' attempt never reaches the UI."""
