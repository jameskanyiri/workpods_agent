from langchain.agents import AgentState
from typing import Annotated, NotRequired

from src.state.schema import VFile, Todo
from src.state.utils import merge_vfs, replace_todos_list


class GeneralSubAgentState(AgentState):
    """State for the general-purpose subagent. Includes todos, VFS, and active skill."""
    todos: Annotated[NotRequired[list[Todo]], replace_todos_list]
    vfs: Annotated[NotRequired[dict[str, VFile]], merge_vfs]
    active_skill: NotRequired[str]
