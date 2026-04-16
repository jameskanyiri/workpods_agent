import os
import re

from src.middleware.skills_middleware.schema import SkillMetadata


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


def discover_skills(skills_dir: str) -> list[SkillMetadata]:
    """Scan a skills directory and return metadata for all available skills.

    Args:
        skills_dir: Absolute path to the skills directory.

    Returns:
        List of skill metadata parsed from SKILL.md frontmatter.
    """
    skills: list[SkillMetadata] = []

    if not os.path.isdir(skills_dir):
        return skills

    for dir_name in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, dir_name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue

        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()

        fm = _parse_frontmatter(content)
        name = fm.get("name", dir_name.replace("_", "-"))
        description = fm.get("description", "")

        if not name or not description:
            continue

        skills.append(SkillMetadata(
            name=name,
            description=description,
            path=skill_path,
        ))

    return skills
