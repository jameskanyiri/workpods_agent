from langchain.agents.middleware.types import AgentState, ResponseT
from typing import Annotated, NotRequired
from src.middleware.todo.schema import Todo
from langchain.agents.middleware.types import OmitFromInput

class PlanningState(AgentState[ResponseT]):
    """State schema for the todo middleware.

    Type Parameters:
        ResponseT: The type of the structured response. Defaults to `Any`.
    """

    todos: Annotated[NotRequired[list[Todo]], OmitFromInput]
    """List of todo items for tracking task progress."""