from langchain.agents.middleware.types import AgentState
from typing import Annotated, NotRequired

from src.middleware.skills_middleware.schema import SkillMetadata


def _replace_skill_metadata(
    left: list[SkillMetadata] | None,
    right: list[SkillMetadata] | None,
) -> list[SkillMetadata]:
    """Reducer: right replaces left entirely."""
    if right is None:
        return left or []
    return right


class SkillsState(AgentState):
    """State for the skills middleware."""

    skills_metadata: Annotated[NotRequired[list[SkillMetadata]], _replace_skill_metadata]
    """Discovered skill metadata from configured sources."""
