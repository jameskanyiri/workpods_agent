"""
Activate Skill Tool

A tool for activating skill instructions and workflows into context.
"""

from .description import ACTIVATE_SKILL_TOOL_DESCRIPTION
from .tool import activate_skill

__all__ = [
    "ACTIVATE_SKILL_TOOL_DESCRIPTION",
    "activate_skill",
]
