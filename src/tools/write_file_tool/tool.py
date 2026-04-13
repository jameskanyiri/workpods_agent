import os

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import WRITE_FILE_TOOL_DESCRIPTION

SKILLS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


@tool(description=WRITE_FILE_TOOL_DESCRIPTION)
def write_file(
    display_name: str = "Creating file",
    file_path: str = "",
    content: str = "",
    storage_type: str = "vfs",
    runtime: ToolRuntime = None,
) -> Command:
    """Create a new file in the local skills directory or the virtual filesystem."""

    if storage_type == "local":
        return _write_local(file_path, content, runtime)

    return _write_vfs(file_path, content, runtime)


def _write_local(file_path: str, content: str, runtime: ToolRuntime) -> Command:
    """Write a file to the local skills directory."""
    clean = file_path.strip("/")
    full_path = os.path.normpath(os.path.join(SKILLS_DIR, clean))

    if not full_path.startswith(SKILLS_DIR):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Access denied: path '{file_path}' is outside the skills directory.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    if os.path.isfile(full_path):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"File already exists at '{file_path}'. Use edit_file to modify it.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Created file at '{file_path}' ({len(content)} characters).",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )


def _write_vfs(file_path: str, content: str, runtime: ToolRuntime) -> Command:
    """Write a file to the virtual filesystem."""
    vfs: dict = runtime.state.get("vfs", {})

    if file_path in vfs:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"File already exists at '{file_path}'. Use edit_file to modify it.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    vfile = {"path": file_path, "content": content}

    return Command(
        update={
            "vfs": {file_path: vfile},
            "messages": [
                ToolMessage(
                    content=f"Created file at '{file_path}' ({len(content)} characters).",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
