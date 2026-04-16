import os
from langchain.tools import tool, ToolRuntime

from src.middleware.filesystem_middleware.tools.read_file.description import READ_FILE_TOOL_DESCRIPTION
from src.middleware.filesystem_middleware.state import FilesystemState
from src.middleware.filesystem_middleware.config import DEFAULT_READ_OFFSET, DEFAULT_READ_LIMIT, SKILLS_DIR


def _paginate(file_path: str, content: str, offset: int, limit: int) -> str:
    """Format file content with line numbers and pagination."""
    if not content:
        return "System reminder: File exists but has empty contents"

    lines = content.splitlines()
    total_lines = len(lines)

    selected = lines[offset:offset + limit]

    if not selected:
        return f"Error: offset {offset} is beyond end of file ({total_lines} lines)"

    numbered = []
    for i, line in enumerate(selected, start=offset + 1):
        numbered.append(f"{i:>6}\t{line}")

    result = "\n".join(numbered)

    if offset + limit < total_lines:
        result += f"\n\n[Showing lines {offset + 1}-{offset + len(selected)} of {total_lines}. Use offset/limit to read more.]"

    return result


@tool(description=READ_FILE_TOOL_DESCRIPTION)
def read_file(
    display_name: str = "Reading",
    file_path: str = "/",
    offset: int = DEFAULT_READ_OFFSET,
    limit: int = DEFAULT_READ_LIMIT,
    runtime: ToolRuntime[None, FilesystemState] = None,
) -> str:
    """Read a file from state or disk (skills directory)."""

    # 1. Try state first
    files: dict = runtime.state.get("files", {})
    if file_path in files:
        content = files[file_path].get("content", "")
        return _paginate(file_path, content, offset, limit)

    # 2. Fall back to disk — resolve relative paths against the skills directory
    if os.path.isabs(file_path):
        normalized = os.path.normpath(file_path)
    else:
        normalized = os.path.normpath(os.path.join(SKILLS_DIR, file_path))

    # Security: only allow reads under the skills directory
    if not normalized.startswith(SKILLS_DIR):
        return f"Error: Access denied — disk reads are restricted to the skills directory: '{SKILLS_DIR}'"

    if os.path.isfile(normalized):
        with open(normalized, "r", encoding="utf-8") as f:
            content = f.read()
        return _paginate(file_path, content, offset, limit)

    return f"Error: File not found: '{file_path}'"
