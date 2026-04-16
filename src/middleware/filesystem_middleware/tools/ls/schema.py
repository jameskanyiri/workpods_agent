from pydantic import BaseModel, Field


class LsSchema(BaseModel):
    """Input schema for the `ls` tool."""

    path: str = Field(description="Absolute path to the directory to list. Must be absolute, not relative.")
