from langchain.agents import AgentState
from typing import NotRequired
from typing_extensions import TypedDict


class SummarizationEvent(TypedDict):
    """Record of a summarization that occurred.

    Stored in state so subsequent turns can reconstruct which messages
    were compacted and where the full history lives.
    """

    cutoff_index: int
    """Index in the original messages list where summarization cut off."""

    summary_text: str
    """The generated summary text that replaced the old messages."""

    history_path: str | None
    """VFS path where the full evicted conversation was saved, or None if offload failed."""


class SummarizationState(AgentState):
    """State extension for conversation summarization."""

    _summarization_event: NotRequired[SummarizationEvent | None]
    """Most recent summarization event. Private — not exposed to the agent."""

    _total_summarizations: NotRequired[int]
    """Running count of how many times summarization has fired."""
