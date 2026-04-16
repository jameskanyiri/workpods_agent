from pydantic import BaseModel, Field


class WriteFileSchema(BaseModel):
    """Input schema for the `write_file` tool."""

    file_path: str = Field(description="Absolute path where the file should be created. Must be absolute, not relative.")
    content: str = Field(description="The text content to write to the file. This parameter is required.")
