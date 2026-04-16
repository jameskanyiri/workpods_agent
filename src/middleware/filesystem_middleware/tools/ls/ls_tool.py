from langchain.tools import tool, ToolRuntime

from src.middleware.filesystem_middleware.tools.ls.description import LIST_FILES_TOOL_DESCRIPTION
from src.middleware.filesystem_middleware.state import FilesystemState


@tool(description=LIST_FILES_TOOL_DESCRIPTION)
def ls(
    display_name: str = "Browsing",
    path: str = "/",
    runtime: ToolRuntime[None, FilesystemState] = None,
) -> str:
    """List all files in a directory."""

    files: dict = runtime.state.get("files", {})

    # Normalize path to ensure consistent matching
    if not path.endswith("/"):
        path = path + "/"

    # Find entries that are direct children of the given path
    entries = []
    seen_dirs = set()

    for file_path in sorted(files.keys()):
        if not file_path.startswith(path):
            continue

        # Get the relative part after the search path
        relative = file_path[len(path):]

        if "/" in relative:
            # It's in a subdirectory — show the directory name
            dir_name = relative.split("/")[0] + "/"
            if dir_name not in seen_dirs:
                seen_dirs.add(dir_name)
                entries.append(f"{path}{dir_name}")
        else:
            # Direct child file
            entries.append(file_path)

    if not entries:
        return f"No files found in '{path}'"

    return "\n".join(entries)
