import fnmatch as fn
import os

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import GREP_TOOL_DESCRIPTION

SKILLS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


@tool(description=GREP_TOOL_DESCRIPTION)
def grep_tool(
    display_name: str = "Searching content",
    pattern: str = "",
    runtime: ToolRuntime = None,
    glob: str = "",
    output_mode: str = "files_with_matches",
    storage_type: str = "vfs",
) -> Command:
    """Search for text across files. Use storage_type to select local skills or VFS."""

    if storage_type == "local":
        return _grep_local(pattern, glob, output_mode, runtime)

    return _grep_vfs(pattern, glob, output_mode, runtime)


def _grep_local(pattern: str, glob_pattern: str, output_mode: str, runtime: ToolRuntime) -> Command:
    """Search for a text pattern across files in the local skills directory."""
    results: list[str] = []

    for root, _dirs, files in os.walk(SKILLS_DIR):
        for name in files:
            if name.startswith("."):
                continue
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, SKILLS_DIR)

            if glob_pattern and not (fn.fnmatch(rel_path, glob_pattern.strip("/")) or fn.fnmatch(rel_path, glob_pattern)):
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue

            if pattern not in content:
                continue

            if output_mode == "files_with_matches":
                results.append(rel_path)
            elif output_mode == "content":
                for i, line in enumerate(content.splitlines(), start=1):
                    if pattern in line:
                        results.append(f"{rel_path}:{i}: {line}")
            elif output_mode == "count":
                count = content.count(pattern)
                results.append(f"{rel_path}: {count} match(es)")

    if not results:
        response = f"No matches for '{pattern}'"
        if glob_pattern:
            response += f" in files matching '{glob_pattern}'"
    else:
        response = "\n".join(results)

    return Command(
        update={
            "messages": [
                ToolMessage(content=response, tool_call_id=runtime.tool_call_id)
            ]
        }
    )


def _grep_vfs(pattern: str, glob_pattern: str, output_mode: str, runtime: ToolRuntime) -> Command:
    """Search for a text pattern across files in the virtual filesystem."""
    vfs: dict = runtime.state.get("vfs", {})
    results: list[str] = []

    for path, vfile in sorted(vfs.items()):
        if glob_pattern and not (fn.fnmatch(path, glob_pattern) or fn.fnmatch(path.lstrip("/"), glob_pattern)):
            continue

        content = vfile.get("content", "")
        if pattern not in content:
            continue

        if output_mode == "files_with_matches":
            results.append(path)
        elif output_mode == "content":
            for i, line in enumerate(content.splitlines(), start=1):
                if pattern in line:
                    results.append(f"{path}:{i}: {line}")
        elif output_mode == "count":
            count = content.count(pattern)
            results.append(f"{path}: {count} match(es)")

    if not results:
        response = f"No matches for '{pattern}'"
        if glob_pattern:
            response += f" in files matching '{glob_pattern}'"
    else:
        response = "\n".join(results)

    return Command(
        update={
            "messages": [
                ToolMessage(content=response, tool_call_id=runtime.tool_call_id)
            ]
        }
    )
