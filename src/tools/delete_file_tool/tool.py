import os

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import DELETE_FILE_TOOL_DESCRIPTION

SKILLS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


@tool(description=DELETE_FILE_TOOL_DESCRIPTION)
def delete_file(
    display_name: str = "Deleting file",
    file_path: str = "",
    storage_type: str = "vfs",
    runtime: ToolRuntime = None,
) -> Command:
    """Delete a file from the local skills directory or the virtual filesystem."""

    if storage_type == "local":
        return _delete_local(file_path, runtime)

    return _delete_vfs(file_path, runtime)


def _delete_local(file_path: str, runtime: ToolRuntime) -> Command:
    """Delete a file from the local skills directory."""
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

    if not os.path.isfile(full_path):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"File not found: '{file_path}' does not exist.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    os.remove(full_path)

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Deleted file '{file_path}'.",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )


def _delete_vfs(file_path: str, runtime: ToolRuntime) -> Command:
    """Delete a file from the virtual filesystem."""
    vfs: dict = runtime.state.get("vfs", {})

    if file_path not in vfs:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"File not found: '{file_path}' does not exist in the virtual filesystem.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    # Setting content to None signals deletion in merge_vfs
    return Command(
        update={
            "vfs": {file_path: {"path": file_path, "content": None}},
            "messages": [
                ToolMessage(
                    content=f"Deleted file '{file_path}'.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
