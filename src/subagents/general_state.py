from langchain.agents import AgentState
from langchain.agents.middleware.types import OmitFromInput
from typing import Annotated, NotRequired

from src.state.schema import VFile
from src.state.utils import merge_vfs
from src.middleware.todo_middleware.schema import Todo


class GeneralSubAgentState(AgentState):
    """State for the general-purpose subagent. Includes todos, VFS, and active skill."""
    todos: Annotated[NotRequired[list[Todo]], OmitFromInput]
    vfs: Annotated[NotRequired[dict[str, VFile]], merge_vfs]
    active_skill: NotRequired[str]
