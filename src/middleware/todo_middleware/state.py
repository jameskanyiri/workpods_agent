from langchain.agents.middleware.types import AgentState
from typing import Annotated, NotRequired
from src.middleware.todo_middleware.schema import Todo
from langchain.agents.middleware.types import OmitFromInput

class PlanningState(AgentState):
    """State schema for the todo middleware.

    Type Parameters:
        ResponseT: The type of the structured response. Defaults to `Any`.
    """

    todos: Annotated[NotRequired[list[Todo]], OmitFromInput]
    """List of todo items for tracking task progress."""