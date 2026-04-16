from pydantic import BaseModel, Field
from src.middleware.filesystem_middleware.config import DEFAULT_READ_OFFSET, DEFAULT_READ_LIMIT


class ReadFileSchema(BaseModel):
    """Input schema for the `read_file` tool."""

    file_path: str = Field(description="Absolute path to the file to read. Must be absolute, not relative.")
    offset: int = Field(
        default=DEFAULT_READ_OFFSET,
        description="Line number to start reading from (0-indexed). Use for pagination of large files.",
    )
    limit: int = Field(
        default=DEFAULT_READ_LIMIT,
        description="Maximum number of lines to read. Use for pagination of large files.",
    )
