from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable, Awaitable


@wrap_model_call
async def inject_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
) -> ModelResponse:
    """Inject the active skill instructions, data files, and plans into the model context."""

    active_skill = request.state.get("active_skill", "")
    vfs: dict = request.state.get("vfs", {})

    context_parts: list[str] = []

    if active_skill:
        context_parts.append(
            "## Active Skill\n\n"
            "You are currently operating under the following skill. "
            "Follow these instructions exactly.\n\n"
            f"{active_skill}"
        )

    # Inject plan files from VFS
    plan_files = {
        path: vfile for path, vfile in vfs.items()
        if path.startswith("/plans/") and vfile.get("content")
    }
    if plan_files:
        plans_section = "## Active Plans\n\nYou have the following plans. Use them to guide your next steps.\n\n"
        for path, vfile in plan_files.items():
            plans_section += f"### `{path}`\n\n{vfile['content']}\n\n"
        context_parts.append(plans_section)

    # Inject data files from VFS
    data_files = {
        path: vfile for path, vfile in vfs.items()
        if path.startswith("/data/") and vfile.get("content")
    }
    if data_files:
        data_section = "## Data Files\n\nYou have access to the following data files. Reference them when answering questions.\n\n"
        for path in data_files:
            data_section += f"- `{path}`\n"
        context_parts.append(data_section)

    if context_parts:
        preamble = (
            "[This is your current workspace context. "
            "Keep this in mind as you work.]\n\n"
        )
        combined_context = preamble + "\n\n".join(context_parts)
        messages = [
            *request.messages,
            {"role": "user", "content": combined_context},
        ]
        request = request.override(messages=messages)

    return await handler(request)
