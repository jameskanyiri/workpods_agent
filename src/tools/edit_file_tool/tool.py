import os

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import EDIT_FILE_TOOL_DESCRIPTION

SKILLS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


def _error(msg: str, runtime: ToolRuntime) -> Command:
    return Command(
        update={
            "messages": [
                ToolMessage(content=msg, tool_call_id=runtime.tool_call_id)
            ]
        }
    )


def _validate_edit(file_path: str, content: str, old_string: str) -> str | None:
    """Validate the replacement. Returns error message or None."""
    count = content.count(old_string)
    if count == 0:
        return f"old_string not found in '{file_path}'."
    if count > 1:
        return f"old_string matches {count} times in '{file_path}'. Provide more context to make it unique."
    return None


@tool(description=EDIT_FILE_TOOL_DESCRIPTION)
def edit_file(
    display_name: str = "Editing file",
    file_path: str = "",
    old_string: str = "",
    new_string: str = "",
    storage_type: str = "vfs",
    runtime: ToolRuntime = None,
) -> Command:
    """Replace a string in a file. Use storage_type to select local skills or VFS."""

    if storage_type == "local":
        return _edit_local(file_path, old_string, new_string, runtime)

    return _edit_vfs(file_path, old_string, new_string, runtime)


def _edit_local(file_path: str, old_string: str, new_string: str, runtime: ToolRuntime) -> Command:
    """Edit a file in the local skills directory."""
    clean = file_path.strip("/")
    full_path = os.path.normpath(os.path.join(SKILLS_DIR, clean))

    if not full_path.startswith(SKILLS_DIR):
        return _error(f"Access denied: path '{file_path}' is outside the skills directory.", runtime)

    if not os.path.isfile(full_path):
        return _error(f"File not found: '{file_path}'", runtime)

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    err = _validate_edit(file_path, content, old_string)
    if err:
        return _error(err, runtime)

    updated_content = content.replace(old_string, new_string, 1)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Edited '{file_path}' successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )


def _edit_vfs(file_path: str, old_string: str, new_string: str, runtime: ToolRuntime) -> Command:
    """Edit a file in the virtual filesystem."""
    vfs: dict = runtime.state.get("vfs", {})

    if file_path not in vfs:
        return _error(f"File not found: '{file_path}'", runtime)

    content = vfs[file_path]["content"]

    err = _validate_edit(file_path, content, old_string)
    if err:
        return _error(err, runtime)

    updated_content = content.replace(old_string, new_string, 1)
    vfile = {"path": file_path, "content": updated_content}

    return Command(
        update={
            "vfs": {file_path: vfile},
            "messages": [
                ToolMessage(
                    content=f"Edited '{file_path}' successfully.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
