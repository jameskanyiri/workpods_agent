from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import TODO_TOOL_DESCRIPTION as TOOL_DESCRIPTION
from .schema import TodoItem


@tool(description=TOOL_DESCRIPTION)
def write_todos(
    display_name: str = "Updating tasks",
    todos: list[TodoItem] = None,
    runtime: ToolRuntime = None,
) -> Command:
    """
    Replace the current todo list in state.
    """
    tool_call_id = runtime.tool_call_id

    todos_dump = [t.model_dump() for t in (todos or [])]

    return Command(
        update={
            "todos": todos_dump,
            "messages": [
                ToolMessage(
                    content=f"Updated todo list to {todos_dump}",
                    tool_call_id=tool_call_id,
                    name=display_name,
                )
            ],
        }
    )
