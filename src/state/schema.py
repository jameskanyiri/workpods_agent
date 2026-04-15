from typing import TypedDict, Literal


class VFile(TypedDict):
    """A virtual file in the in-state filesystem."""
    path: str
    content: str


class ScriptResult(TypedDict):
    """Standard response format that all skill scripts must return as JSON to stdout.

    Fields:
        status:  "success" or "error"
        message: Human-readable summary of what the script generated.
        type:    File extension / format hint (e.g. "geojson", "json", "md", "csv").
        data:    The actual payload to be persisted in the VFS.
    """
    status: Literal["success", "error"]
    message: str
    type: str
    data: object