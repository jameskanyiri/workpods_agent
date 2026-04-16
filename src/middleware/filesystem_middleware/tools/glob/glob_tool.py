import fnmatch
import pathlib

from langchain.tools import tool, ToolRuntime

from src.middleware.filesystem_middleware.tools.glob.description import GLOB_TOOL_DESCRIPTION
from src.middleware.filesystem_middleware.state import FilesystemState
from src.middleware.filesystem_middleware.config import SKILLS_DIR


@tool(description=GLOB_TOOL_DESCRIPTION)
def glob(
    display_name: str = "Looking up",
    pattern: str = "**/*",
    path: str = "/",
    runtime: ToolRuntime[None, FilesystemState] = None,
) -> str:
    """Find files matching a glob pattern in state and on disk (skills directory)."""

    files: dict = runtime.state.get("files", {})

    # Normalize path
    if not path.endswith("/"):
        path = path + "/"

    # Build full pattern
    full_pattern = f"{path}{pattern}" if not pattern.startswith("/") else pattern

    # 1. Search virtual filesystem state
    matches = [
        file_path for file_path in sorted(files.keys())
        if fnmatch.fnmatch(file_path, full_pattern)
    ]

    # 2. Fall back to disk (skills directory) if no state matches
    if not matches:
        skills_path = pathlib.Path(SKILLS_DIR)
        if skills_path.is_dir():
            disk_matches = sorted(
                str(p) for p in skills_path.rglob(pattern)
                if p.is_file()
            )
            if disk_matches:
                return "\n".join(disk_matches)

    if not matches:
        return f"No files matching pattern '{pattern}' in '{path}'"

    return "\n".join(matches)
