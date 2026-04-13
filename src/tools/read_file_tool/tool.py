import os

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import READ_FILE_TOOL_DESCRIPTION

SKILLS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


@tool(description=READ_FILE_TOOL_DESCRIPTION)
def read_file(
    display_name: str = "Reading file",
    file_path: str = "",
    runtime: ToolRuntime = None,
    offset: int = 0,
    limit: int = 100,
    storage_type: str = "vfs",
) -> Command:
    """Read a file from the local skills directory or the virtual filesystem."""

    if storage_type == "local":
        return _read_local(file_path, offset, limit, runtime)

    return _read_vfs(file_path, offset, limit, runtime)


def _read_local(file_path: str, offset: int, limit: int, runtime: ToolRuntime) -> Command:
    """Read a file from the local skills directory."""
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
                        content=f"File not found: '{file_path}'",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    return _paginate(file_path, content, offset, limit, runtime)


def _read_vfs(file_path: str, offset: int, limit: int, runtime: ToolRuntime) -> Command:
    """Read a file from the virtual filesystem."""
    vfs: dict = runtime.state.get("vfs", {})

    if file_path not in vfs:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"File not found: '{file_path}'",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    content = vfs[file_path]["content"]
    return _paginate(file_path, content, offset, limit, runtime)


def _paginate(file_path: str, content: str, offset: int, limit: int, runtime: ToolRuntime) -> Command:
    """Format file content with line numbers and pagination."""
    lines = content.splitlines(keepends=True)
    total_lines = len(lines)

    selected = lines[offset : offset + limit]
    numbered = []
    for i, line in enumerate(selected, start=offset + 1):
        numbered.append(f"{i:>6}\t{line.rstrip()}")

    header = f"File: {file_path} | Lines {offset + 1}-{offset + len(selected)} of {total_lines}"
    result = header + "\n" + "\n".join(numbered)

    return Command(
        update={
            "messages": [
                ToolMessage(content=result, tool_call_id=runtime.tool_call_id)
            ]
        }
    )
