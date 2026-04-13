import os

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import LIST_FILES_TOOL_DESCRIPTION

SKILLS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


def _ls_local(path: str, runtime: ToolRuntime) -> Command:
    """List files in the local skills directory."""
    clean = path.strip("/")
    full_path = os.path.normpath(os.path.join(SKILLS_DIR, clean)) if clean else SKILLS_DIR

    # Security: ensure the resolved path stays within SKILLS_DIR
    if not full_path.startswith(SKILLS_DIR):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Access denied: path '{path}' is outside the skills directory.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    if not os.path.isdir(full_path):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Directory not found: '{path}'",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    entries: list[str] = []
    for name in sorted(os.listdir(full_path)):
        if name.startswith("."):
            continue
        if os.path.isdir(os.path.join(full_path, name)):
            entries.append(name + "/")
        else:
            entries.append(name)

    if not entries:
        content = f"No files found at '{path.rstrip('/')}'"
    else:
        sorted_entries = sorted(entries, key=lambda e: (not e.endswith("/"), e))
        display_path = path.rstrip("/") or "/"
        content = f"Contents of '{display_path}':\n" + "\n".join(f"  {e}" for e in sorted_entries)

    return Command(
        update={
            "messages": [
                ToolMessage(content=content, tool_call_id=runtime.tool_call_id)
            ]
        }
    )


def _ls_vfs(path: str, runtime: ToolRuntime) -> Command:
    """List files in the virtual filesystem."""
    vfs: dict = runtime.state.get("vfs", {})

    # Normalize path
    if not path or path == ".":
        path = "/"
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path = path + "/"
    if path == "//":
        path = "/"

    entries: set[str] = set()
    for file_path in vfs:
        if path == "/" or file_path.startswith(path):
            remainder = file_path[len(path):] if path != "/" else file_path.lstrip("/")
            if not remainder:
                continue
            parts = remainder.split("/")
            if len(parts) == 1:
                entries.add(parts[0])
            else:
                entries.add(parts[0] + "/")

    if not entries:
        content = f"No files found at '{path.rstrip('/')}'"
    else:
        sorted_entries = sorted(entries, key=lambda e: (not e.endswith("/"), e))
        content = f"Contents of '{path.rstrip('/')}':\n" + "\n".join(f"  {e}" for e in sorted_entries)

    return Command(
        update={
            "messages": [
                ToolMessage(content=content, tool_call_id=runtime.tool_call_id)
            ]
        }
    )


@tool(description=LIST_FILES_TOOL_DESCRIPTION)
def ls_tool(
    display_name: str = "Listing files",
    path: str = "/",
    storage_type: str = "vfs",
    runtime: ToolRuntime = None,
) -> Command:
    """List files and directories from the local skills directory or virtual filesystem."""

    if storage_type == "local":
        return _ls_local(path, runtime)

    return _ls_vfs(path, runtime)
