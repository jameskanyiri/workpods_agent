from langchain.agents.middleware.types import (
    AgentMiddleware,
    ContextT,
    ModelRequest,
)
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from src.middleware.todo.state import PlanningState
from src.middleware.todo.write_todo_tool import write_todos
from src.middleware.todo.prompt import WRITE_TODOS_SYSTEM_PROMPT
from typing_extensions import override


class TodoListMiddleware(
    AgentMiddleware[PlanningState, ContextT]
):
    """
    Middleware that provides todo list management capabilities to agents.

    This middleware adds a `write_todos` tool that allows agents to create and manage
    structured task lists for complex multi-step operations. It's designed to help
    agents track progress, organize complex tasks, and provide users with visibility
    into task completion status.

    The middleware automatically injects system prompts that guide the agent on when
    and how to use the todo functionality effectively. It also enforces that the
    `write_todos` tool is called at most once per model turn, since the tool replaces
    the entire todo list and parallel calls would create ambiguity about precedence.

    """

    state_schema = PlanningState

    def __init__(self) -> None:
        super().__init__()
        self.tools = [write_todos]

    def _inject_system_prompt(self, request: ModelRequest) -> ModelRequest:

        extra = {"type": "text", "text": WRITE_TODOS_SYSTEM_PROMPT}

        if request.system_message is not None:
            new_content = [*request.system_message.content_blocks, extra]
        else:
            new_content = [extra]

        return request.override(system_message=SystemMessage(content=new_content))


    async def awrap_model_call(self, request, handler):
        return await handler(self._inject_system_prompt(request))

    def check_for_parallel_tool_calls(self, state: PlanningState) -> dict | None:
        messages = state['messages']

        if not messages:
            return None

        last_ai_message = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)

        if not last_ai_message or not last_ai_message.tool_calls:
            return None

        dupes = [tc for tc in last_ai_message.tool_calls if tc["name"] == "write_todos"]


        if len(dupes) > 1:
            return {
                "messages": [
                    ToolMessage(
                        content="Error: `write_todos` must not be called in parallel.",
                        tool_call_id=tc["id"],
                        status="error",
                    )
                    for tc in dupes
                ]
            }
        return None


    @override
    async def aafter_model(self, state, runtime):
        return self.check_for_parallel_tool_calls(state)

