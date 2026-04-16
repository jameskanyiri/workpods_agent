from pydantic import BaseModel, Field


class GlobSchema(BaseModel):
    """Input schema for the `glob` tool."""

    pattern: str = Field(description="Glob pattern to match files (e.g., '**/*.py', '*.txt', '/subdir/**/*.md').")
    path: str = Field(default="/", description="Base directory to search from. Defaults to root '/'.")
