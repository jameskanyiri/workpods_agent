from typing import TypedDict, NotRequired


class FileData(TypedDict):
    """Data structure for storing file contents with metadata."""

    content: str
    """File content as a plain string (utf-8 text or base64-encoded binary)."""

    encoding: str
    """Content encoding: `"utf-8"` for text, `"base64"` for binary."""

    created_at: NotRequired[str]
    """ISO 8601 timestamp of file creation."""

    modified_at: NotRequired[str]
    """ISO 8601 timestamp of last modification."""