from typing import Literal
from pydantic import BaseModel, Field


class GrepSchema(BaseModel):
    """Input schema for the `grep` tool."""

    pattern: str = Field(description="Text pattern to search for (literal string, not regex).")
    path: str | None = Field(default=None, description="Directory to search in. Defaults to current working directory.")
    glob: str | None = Field(default=None, description="Glob pattern to filter which files to search (e.g., '*.py').")
    output_mode: Literal["files_with_matches", "content", "count"] = Field(
        default="files_with_matches",
        description="Output format: 'files_with_matches' (file paths only, default), 'content' (matching lines with context), 'count' (match counts per file).",
    )
