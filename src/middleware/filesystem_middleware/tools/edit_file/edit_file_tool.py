from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Any

from src.middleware.filesystem_middleware.tools.edit_file.description import EDIT_FILE_TOOL_DESCRIPTION
from src.middleware.filesystem_middleware.state import FilesystemState


@tool(description=EDIT_FILE_TOOL_DESCRIPTION)
def edit_file(
    display_name: str = "Updating",
    file_path: str = "/",
    old_string: str = "",
    new_string: str = "",
    replace_all: bool = False,
    runtime: ToolRuntime[None, FilesystemState] = None,
) -> Command[Any]:
    """Perform exact string replacements in a file."""

    files: dict = runtime.state.get("files", {})

    if file_path not in files:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: File not found: '{file_path}'",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    content = files[file_path].get("content", "")

    if old_string == new_string:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: old_string and new_string must be different",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    if old_string not in content:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: old_string not found in '{file_path}'",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    count = content.count(old_string)

    if not replace_all and count > 1:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: old_string found {count} times in '{file_path}'. Use replace_all=True or provide a more unique string.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    if replace_all:
        new_content = content.replace(old_string, new_string)
    else:
        new_content = content.replace(old_string, new_string, 1)

    updated_file = {**files[file_path], "content": new_content}

    return Command(
        update={
            "files": {file_path: updated_file},
            "messages": [
                ToolMessage(
                    content=f"Successfully replaced {count if replace_all else 1} instance(s) in '{file_path}'",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
