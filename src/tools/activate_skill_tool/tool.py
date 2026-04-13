import os
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import ACTIVATE_SKILL_TOOL_DESCRIPTION
from src.utils.skills_registry import get_skill_names_to_dirs, SKILLS_DIR


@tool(description=ACTIVATE_SKILL_TOOL_DESCRIPTION)
def activate_skill(
    display_name: str = "Activating skill",
    skill_name: str = "",
    runtime: ToolRuntime = None,
) -> Command:
    """Activate a skill's full instructions and workflow into context."""

    skill_map = get_skill_names_to_dirs()
    dir_name = skill_map.get(skill_name)

    if dir_name is None:
        available = ", ".join(sorted(skill_map.keys()))
        content = f"Unknown skill '{skill_name}'. Available skills: {available}"
        return Command(
            update={
                "messages": [
                    ToolMessage(content=content, tool_call_id=runtime.tool_call_id)
                ]
            }
        )

    skill_path = os.path.join(SKILLS_DIR, dir_name, "SKILL.md")

    if not os.path.exists(skill_path):
        content = f"Skill file not found for '{skill_name}'."
        return Command(
            update={
                "messages": [
                    ToolMessage(content=content, tool_call_id=runtime.tool_call_id)
                ]
            }
        )

    with open(skill_path, "r", encoding="utf-8") as f:
        skill_content = f.read()

    return Command(
        update={
            "active_skill": skill_content,
            "messages": [
                ToolMessage(content=skill_content, tool_call_id=runtime.tool_call_id)
            ]
        }
    )
