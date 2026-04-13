from langchain.agents import AgentState
from typing import Annotated, NotRequired

from src.state.schema import VFile
from src.state.utils import merge_vfs


class SubAgentState(AgentState):
    """Minimal state for subagents. Only messages (inherited) and VFS."""
    vfs: Annotated[NotRequired[dict[str, VFile]], merge_vfs]
