from typing import TypedDict, Literal
from langchain.agents.middleware.types import AgentState, ResponseT,OmitFromInput
from typing import Annotated, NotRequired

class Todo(TypedDict):
    """A single todo item with id, label and status"""

    id: str
    """Unique identifier for the todo item"""

    content: str
    """The content/description of the todo item."""

    status: Literal["pending", "in_progress", "completed"]
    """Task status: pending, in_progress, or completed."""





class WriteTodoInput(TypedDict):
    """Input schema for the write_todos tool"""

    todos: list[Todo]
    """List of todo items to write"""