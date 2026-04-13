from langchain.agents import AgentState
from typing import Annotated, NotRequired

from src.state.schema import Todo, VFile
from src.state.utils import replace_todos_list, merge_vfs


class CustomState(AgentState):
    todos: Annotated[NotRequired[list[Todo]], replace_todos_list]
    active_skill: NotRequired[str]
    vfs: Annotated[NotRequired[dict[str, VFile]], merge_vfs]



