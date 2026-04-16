from pydantic import BaseModel, Field


class EditFileSchema(BaseModel):
    """Input schema for the `edit_file` tool."""

    file_path: str = Field(description="Absolute path to the file to edit. Must be absolute, not relative.")
    old_string: str = Field(description="The exact text to find and replace. Must be unique in the file unless replace_all is True.")
    new_string: str = Field(description="The text to replace old_string with. Must be different from old_string.")
    replace_all: bool = Field(
        default=False,
        description="If True, replace all occurrences of old_string. If False (default), old_string must be unique.",
    )
