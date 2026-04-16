import fnmatch
from langchain.tools import tool, ToolRuntime

from src.middleware.filesystem_middleware.tools.grep.description import GREP_TOOL_DESCRIPTION
from src.middleware.filesystem_middleware.state import FilesystemState


@tool(description=GREP_TOOL_DESCRIPTION)
def grep(
    display_name: str = "Looking up",
    pattern: str = "",
    path: str | None = None,
    glob: str | None = None,
    output_mode: str = "files_with_matches",
    runtime: ToolRuntime[None, FilesystemState] = None,
) -> str:
    """Search for a text pattern across files."""

    files: dict = runtime.state.get("files", {})

    # Filter files by path prefix
    search_path = path or "/"
    if not search_path.endswith("/"):
        search_path = search_path + "/"

    candidates = {
        fp: data for fp, data in files.items()
        if fp.startswith(search_path)
    }

    # Filter by glob pattern if provided
    if glob:
        candidates = {
            fp: data for fp, data in candidates.items()
            if fnmatch.fnmatch(fp, f"**/{glob}") or fnmatch.fnmatch(fp.split("/")[-1], glob)
        }

    if not candidates:
        return f"No files to search in '{search_path}'"

    results = []

    for file_path, file_data in sorted(candidates.items()):
        content = file_data.get("content", "")
        lines = content.splitlines()

        matching_lines = [
            (i + 1, line) for i, line in enumerate(lines)
            if pattern in line
        ]

        if not matching_lines:
            continue

        if output_mode == "files_with_matches":
            results.append(file_path)
        elif output_mode == "count":
            results.append(f"{file_path}: {len(matching_lines)}")
        elif output_mode == "content":
            for line_no, line in matching_lines:
                results.append(f"{file_path}:{line_no}: {line}")

    if not results:
        return f"No matches for '{pattern}'"

    return "\n".join(results)
