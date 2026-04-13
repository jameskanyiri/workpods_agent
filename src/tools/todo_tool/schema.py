from pydantic import BaseModel, Field
from typing import Literal


class TodoItem(BaseModel):
    """
    A single todo item with id, label, status, and description.
    """

    id: str = Field(description="Unique identifier for the task (e.g. '1', '2').")
    label: str = Field(description="Short display title, 5-8 words max (e.g. 'Draft executive summary').")
    status: Literal["pending", "in_progress", "completed"] = Field(
        description="Task status: pending, in_progress, or completed."
    )
    description: str = Field(
        description="REQUIRED for all statuses. Detailed breakdown: what this task involves, inputs needed, expected output. For completed tasks: what was done, decisions made, files created.",
    )