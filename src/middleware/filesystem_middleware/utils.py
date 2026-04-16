from src.middleware.filesystem_middleware.schema import FileData

from typing import cast
from langchain_core.messages import HumanMessage, ContentBlock, BaseMessage

from src.middleware.filesystem_middleware.config import MAX_LINE_LENGTH, LINE_NUMBER_WIDTH
from src.middleware.filesystem_middleware.prompt import TOO_LARGE_HUMAN_MSG


def file_data_reducer(left: dict[str, FileData] | None, right: dict[str, FileData | None]) -> dict[str, FileData]:
    """Merge file updates with support for deletions.

    This reducer enables file deletion by treating `None` values in the right
    dictionary as deletion markers. It's designed to work with LangGraph's
    state management where annotated reducers control how state updates merge.

    Args:
        left: Existing files dictionary. May be `None` during initialization.
        right: New files dictionary to merge. Files with `None` values are
            treated as deletion markers and removed from the result.

    Returns:
        Merged dictionary where right overwrites left for matching keys,
        and `None` values in right trigger deletions.

    Example:
        ```python
        existing = {"/file1.txt": FileData(...), "/file2.txt": FileData(...)}
        updates = {"/file2.txt": None, "/file3.txt": FileData(...)}
        result = file_data_reducer(existing, updates)
        # Result: {"/file1.txt": FileData(...), "/file3.txt": FileData(...)}
        ```
    """
    if left is None:
        return {k: v for k, v in right.items() if v is not None}

    result = {**left}
    for key, value in right.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = value
    return result


def build_evicted_human_content(
    message: HumanMessage,
    replacement_text: str,
) -> str | list[ContentBlock]:
    """Build replacement content for an evicted HumanMessage, preserving non-text blocks.

    For plain string content, returns the replacement text directly. For list content
    with mixed block types (e.g., text + image), replaces all text blocks with a single
    text block containing the replacement text while keeping non-text blocks intact.

    Args:
        message: The original HumanMessage being evicted.
        replacement_text: The truncation notice and preview text.

    Returns:
        Replacement content: a string or list of content blocks.
    """
    if isinstance(message.content, str):
        return replacement_text
    media_blocks = [block for block in message.content_blocks if block["type"] != "text"]
    if not media_blocks:
        return replacement_text
    return [cast("ContentBlock", {"type": "text", "text": replacement_text}), *media_blocks]


def extract_text_from_message(message: BaseMessage) -> str:
    """Extract text from a message using its `content_blocks` property.

    Joins all text content blocks and ignores non-text blocks (images, audio, etc.)
    so that binary payloads don't inflate the size measurement.

    Args:
        message: The BaseMessage to extract text from.

    Returns:
        Joined text from all text content blocks, or stringified content as fallback.
    """
    texts = [block["text"] for block in message.content_blocks if block["type"] == "text"]
    return "\n".join(texts)


def format_content_with_line_numbers(
    content: str | list[str],
    start_line: int = 1,
) -> str:
    """Format file content with line numbers (cat -n style).

    Chunks lines longer than MAX_LINE_LENGTH with continuation markers (e.g., 5.1, 5.2).

    Args:
        content: File content as string or list of lines
        start_line: Starting line number (default: 1)

    Returns:
        Formatted content with line numbers and continuation markers
    """
    if isinstance(content, str):
        lines = content.split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
    else:
        lines = content

    result_lines = []
    for i, line in enumerate(lines):
        line_num = i + start_line

        if len(line) <= MAX_LINE_LENGTH:
            result_lines.append(f"{line_num:{LINE_NUMBER_WIDTH}d}\t{line}")
        else:
            # Split long line into chunks with continuation markers
            num_chunks = (len(line) + MAX_LINE_LENGTH - 1) // MAX_LINE_LENGTH
            for chunk_idx in range(num_chunks):
                start = chunk_idx * MAX_LINE_LENGTH
                end = min(start + MAX_LINE_LENGTH, len(line))
                chunk = line[start:end]
                if chunk_idx == 0:
                    # First chunk: use normal line number
                    result_lines.append(f"{line_num:{LINE_NUMBER_WIDTH}d}\t{chunk}")
                else:
                    # Continuation chunks: use decimal notation (e.g., 5.1, 5.2)
                    continuation_marker = f"{line_num}.{chunk_idx}"
                    result_lines.append(f"{continuation_marker:>{LINE_NUMBER_WIDTH}}\t{chunk}")

    return "\n".join(result_lines)

def create_content_preview(content_str: str, *, head_lines: int = 5, tail_lines: int = 5) -> str:
    """Create a preview of content showing head and tail with truncation marker.

    Args:
        content_str: The full content string to preview.
        head_lines: Number of lines to show from the start.
        tail_lines: Number of lines to show from the end.

    Returns:
        Formatted preview string with line numbers.
    """
    lines = content_str.splitlines()

    if len(lines) <= head_lines + tail_lines:
        # If file is small enough, show all lines
        preview_lines = [line[:1000] for line in lines]
        return format_content_with_line_numbers(preview_lines, start_line=1)

    # Show head and tail with truncation marker
    head = [line[:1000] for line in lines[:head_lines]]
    tail = [line[:1000] for line in lines[-tail_lines:]]

    head_sample = format_content_with_line_numbers(head, start_line=1)
    truncation_notice = f"\n... [{len(lines) - head_lines - tail_lines} lines truncated] ...\n"
    tail_sample = format_content_with_line_numbers(tail, start_line=len(lines) - tail_lines + 1)

    return head_sample + truncation_notice + tail_sample

def build_truncated_human_message(message: HumanMessage, file_path: str) -> HumanMessage:
    """Build a truncated HumanMessage for the model request.

    Computes a preview from the full content still in state and returns a
    lightweight replacement the model will see. Pure string computation — no
    backend I/O.

    Args:
        message: The original HumanMessage (full content in state).
        file_path: The backend path where the content was evicted.

    Returns:
        A new HumanMessage with truncated content and the same `id`.
    """
    content_str = extract_text_from_message(message)
    content_sample = create_content_preview(content_str)
    replacement_text = TOO_LARGE_HUMAN_MSG.format(
        file_path=file_path,
        content_sample=content_sample,
    )
    evicted = build_evicted_human_content(message, replacement_text)
    return message.model_copy(update={"content": evicted})
