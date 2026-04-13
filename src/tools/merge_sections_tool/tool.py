from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import MERGE_SECTIONS_TOOL_DESCRIPTION


@tool(description=MERGE_SECTIONS_TOOL_DESCRIPTION)
def merge_sections(
    section_paths: list[str] = None,
    output_path: str = "",
    separator: str = "\n\n---\n\n",
    display_name: str = "Assembling document",
    runtime: ToolRuntime = None,
) -> Command:
    """Merge multiple VFS section files into a single document."""

    tool_call_id = runtime.tool_call_id

    if not section_paths:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: section_paths is required and must not be empty.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    if not output_path:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: output_path is required.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    vfs: dict = runtime.state.get("vfs", {})

    merged_parts = []
    missing_paths = []

    for path in section_paths:
        vfile = vfs.get(path)
        if vfile and vfile.get("content"):
            merged_parts.append(vfile["content"])
        else:
            missing_paths.append(path)

    if not merged_parts:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: none of the section paths were found in VFS. Missing: {missing_paths}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    merged_content = separator.join(merged_parts)

    # Diagram placeholders ({{diagram-id}}) are left as-is in the merged
    # document.  The frontend resolves them to actual images at render time.

    # Build the merged document VFile
    merged_vfile = {"path": output_path, "content": merged_content}

    # Build result message
    result_parts = [
        f"Merged {len(merged_parts)}/{len(section_paths)} sections into `{output_path}` ({len(merged_content):,} characters)."
    ]
    if missing_paths:
        result_parts.append(f"Missing sections (skipped): {missing_paths}")

    return Command(
        update={
            "vfs": {output_path: merged_vfile},
            "messages": [
                ToolMessage(
                    content="\n".join(result_parts),
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )
