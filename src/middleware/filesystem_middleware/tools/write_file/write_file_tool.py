from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Any

from src.middleware.filesystem_middleware.tools.write_file.description import WRITE_FILE_TOOL_DESCRIPTION
from src.middleware.filesystem_middleware.state import FilesystemState


@tool(description=WRITE_FILE_TOOL_DESCRIPTION)
def write_file(
    display_name: str = "Drafting",
    file_path: str = "/",
    content: str = "",
    runtime: ToolRuntime[None, FilesystemState] = None,
) -> Command[Any]:
    """Write content to a new file in the filesystem."""

    if not file_path.startswith("/"):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Path must be absolute (start with /): '{file_path}'",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    return Command(
        update={
            "files": {
                file_path: {
                    "content": content,
                    "encoding": "utf-8",
                }
            },
            "messages": [
                ToolMessage(
                    content=f"Created file {file_path}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
