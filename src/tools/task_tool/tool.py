from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import TASK_TOOL_DESCRIPTION
from src.subagents.registry import SUBAGENT_REGISTRY
from src.subagents.state import SubAgentState

# Import subagent modules to trigger auto-registration
import src.subagents.writer  # noqa: F401
import src.subagents.researcher  # noqa: F401
import src.subagents.general  # noqa: F401
import src.subagents.planner  # noqa: F401


@tool(description=TASK_TOOL_DESCRIPTION)
async def task(
    agent_name: str = "",
    description: str = "",
    context_data: str = "",
    output_path: str = "",
    display_name: str = "Running task",
    runtime: ToolRuntime = None,
) -> Command:
    """Dispatch a task to a specialized subagent."""

    tool_call_id = runtime.tool_call_id

    # Validate agent name
    if agent_name not in SUBAGENT_REGISTRY:
        available = ", ".join(SUBAGENT_REGISTRY.keys()) or "(none)"
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Unknown agent '{agent_name}'. Available agents: {available}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    config = SUBAGENT_REGISTRY[agent_name]

    # Resolve model: use subagent config model, or inherit from main agent context
    model_name = config.model
    if not model_name:
        model_name = runtime.context.preferred_llm

    # Build the human message for the subagent
    parts = []
    if description:
        parts.append(f"## Task\n\n{description}")
    if context_data:
        parts.append(f"## Data Context\n\n{context_data}")
    if output_path:
        parts.append(f"## Output Path\n\nWrite the completed section to: `{output_path}` (storage_type=\"vfs\")")

    human_message = "\n\n---\n\n".join(parts)

    try:
        # Use per-config state schema, falling back to default SubAgentState
        state_schema = config.state_schema or SubAgentState

        # Create a fresh subagent instance
        sub_kwargs = dict(
            model=init_chat_model(model_name),
            tools=config.tools,
            state_schema=state_schema,
            system_prompt=config.system_prompt,
        )
        sub = create_agent(**sub_kwargs)

        # Pass the main agent's VFS so the subagent can read existing files
        parent_vfs = runtime.state.get("vfs", {})

        # Build initial state based on schema
        initial_state = {
            "messages": [{"role": "user", "content": human_message}],
            "vfs": dict(parent_vfs),
        }
        if hasattr(state_schema, '__annotations__'):
            if 'todos' in state_schema.__annotations__:
                initial_state["todos"] = []
            if 'active_skill' in state_schema.__annotations__:
                initial_state["active_skill"] = ""

        # Invoke with clean state
        result = await sub.ainvoke(
            initial_state,
            config={"recursion_limit": 1000},
        )

        # Extract VFS writes from subagent
        subagent_vfs = result.get("vfs", {})

        # Extract summary from subagent's last message
        messages = result.get("messages", [])
        summary = ""
        if messages:
            last_msg = messages[-1]
            summary = getattr(last_msg, "content", str(last_msg))
            # Truncate long summaries
            if len(summary) > 2000:
                summary = summary[:2000] + "..."

        # Build result message
        files_written = list(subagent_vfs.keys())
        result_parts = [f"Subagent '{agent_name}' completed."]
        if files_written:
            result_parts.append(f"Wrote {len(files_written)} file(s): {files_written}")
        if summary:
            result_parts.append(f"Summary: {summary}")

        return Command(
            update={
                "vfs": subagent_vfs,
                "messages": [
                    ToolMessage(
                        content="\n".join(result_parts),
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Subagent '{agent_name}' failed: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )
