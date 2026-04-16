from typing import TypedDict


class SkillMetadata(TypedDict):
    """Parsed metadata from a SKILL.md frontmatter."""

    name: str
    """Skill identifier (e.g., 'whatsapp-transactions')."""

    description: str
    """What the skill does."""

    path: str
    """Absolute path to the SKILL.md file."""
