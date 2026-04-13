import os
import re
from dataclasses import dataclass

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")


@dataclass
class SkillInfo:
    name: str
    description: str
    dir_name: str


def _parse_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter from a markdown file."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    frontmatter = {}
    for line in match.group(1).strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    return frontmatter


def discover_skills() -> list[SkillInfo]:
    """Scan the skills directory and return metadata for all available skills."""
    skills = []
    if not os.path.isdir(SKILLS_DIR):
        return skills

    for dir_name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, dir_name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
        fm = _parse_frontmatter(content)
        name = fm.get("name", dir_name.replace("_", "-"))
        description = fm.get("description", "")
        skills.append(SkillInfo(name=name, description=description, dir_name=dir_name))

    return skills


def get_skill_names_to_dirs() -> dict[str, str]:
    """Return a mapping of skill name -> directory name."""
    return {s.name: s.dir_name for s in discover_skills()}


def format_skills_for_prompt() -> str:
    """Format the full skills system prompt section with dynamic skill discovery."""
    skills = discover_skills()
    if not skills:
        return "No skills available."

    # Build skills list with paths
    skills_list_lines = []
    for s in skills:
        skill_path = os.path.join(os.path.abspath(SKILLS_DIR), s.dir_name, "SKILL.md")
        skills_list_lines.append(
            f"- **`{s.name}`**: {s.description}\n"
            f"  - Path: `{skill_path}`"
        )
    skills_list = "\n".join(skills_list_lines)

    # Build skills locations
    skills_locations = f"Skills directory: `{os.path.abspath(SKILLS_DIR)}`"

    return (
        "## Skills System\n"
        "\n"
        "You have access to a skills library that provides specialized capabilities and domain knowledge.\n"
        "\n"
        f"{skills_locations}\n"
        "\n"
        "**Available Skills:**\n"
        "\n"
        f"{skills_list}\n"
        "\n"
        "**How to Use Skills (Progressive Disclosure):**\n"
        "\n"
        "Skills follow a **progressive disclosure** pattern — you see their name and description above, "
        "but only load full instructions when needed:\n"
        "\n"
        "1. **Recognize when a skill applies**: Check if the user's task matches a skill's description\n"
        "2. **Load the skill**: Call `activate_skill(skill_name=\"...\")` to get the full workflow instructions\n"
        "3. **Follow the skill's instructions**: The loaded content contains step-by-step workflows, "
        "best practices, and examples\n"
        "\n"
        "**When to Use Skills:**\n"
        "- User's request matches a skill's domain\n"
        "- You need specialized knowledge or structured workflows\n"
        "- A skill provides proven patterns for complex tasks"
    )


def format_skills_for_tool_description() -> str:
    """Format discovered skills as a bullet list for the activate_skill tool description."""
    skills = discover_skills()
    if not skills:
        return "No skills available."

    lines = []
    for s in skills:
        lines.append(f'- "{s.name}" — {s.description}')
    return "\n".join(lines)
