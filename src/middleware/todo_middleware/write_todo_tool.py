from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Any

from src.middleware.todo_middleware.tool_description import WRITE_TODOS_TOOL_DESCRIPTION
from src.middleware.todo_middleware.schema import Todo


@tool(description=WRITE_TODOS_TOOL_DESCRIPTION)
def write_todos(
    display_name: str = "Planning",
    todos: list[Todo] = None,
    runtime: ToolRuntime = None,
) -> Command[Any]:
    """Create and manage a structured task list for your current work session."""

    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(
                    content=f"Updated todo list to {todos}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
