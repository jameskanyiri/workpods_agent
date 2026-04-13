import fnmatch
import os

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import GLOB_TOOL_DESCRIPTION

SKILLS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


@tool(description=GLOB_TOOL_DESCRIPTION)
def glob_tool(
    display_name: str = "Searching files",
    pattern: str = "",
    storage_type: str = "vfs",
    runtime: ToolRuntime = None,
) -> Command:
    """Find files matching a glob pattern. Use storage_type to select local skills or VFS."""

    if storage_type == "local":
        return _glob_local(pattern, runtime)

    return _glob_vfs(pattern, runtime)


def _glob_local(pattern: str, runtime: ToolRuntime) -> Command:
    """Find files in the local skills directory matching a glob pattern."""
    clean = pattern.strip("/")
    matches = []

    for root, _dirs, files in os.walk(SKILLS_DIR):
        for name in files:
            if name.startswith("."):
                continue
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, SKILLS_DIR)
            if fnmatch.fnmatch(rel_path, clean) or fnmatch.fnmatch(rel_path, pattern):
                matches.append(rel_path)

    matches.sort()

    if not matches:
        content = f"No files matching '{pattern}'"
    else:
        content = f"Found {len(matches)} file(s) matching '{pattern}':\n" + "\n".join(f"  {m}" for m in matches)

    return Command(
        update={
            "messages": [
                ToolMessage(content=content, tool_call_id=runtime.tool_call_id)
            ]
        }
    )


def _glob_vfs(pattern: str, runtime: ToolRuntime) -> Command:
    """Find files in the virtual filesystem matching a glob pattern."""
    vfs: dict = runtime.state.get("vfs", {})

    matches = sorted(
        path for path in vfs
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path.lstrip("/"), pattern)
    )

    if not matches:
        content = f"No files matching '{pattern}'"
    else:
        content = f"Found {len(matches)} file(s) matching '{pattern}':\n" + "\n".join(f"  {m}" for m in matches)

    return Command(
        update={
            "messages": [
                ToolMessage(content=content, tool_call_id=runtime.tool_call_id)
            ]
        }
    )
