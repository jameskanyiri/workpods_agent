from pydantic import BaseModel, Field
from typing import Literal


class Question(BaseModel):
    """A single question with options for the user to answer."""

    question: str = Field(
        description="The question text shown to the user. Use plain, non-technical language."
    )
    type: Literal["single_select", "multi_select", "rank_priorities"] = Field(
        default="single_select",
        description=(
            "How the user answers: "
            "single_select = pick one option, "
            "multi_select = pick one or more, "
            "rank_priorities = drag to reorder by priority."
        ),
    )
    options: list[str] = Field(
        description="2 to 4 answer choices. Keep labels short and clear.",
        min_length=2,
        max_length=4,
    )
