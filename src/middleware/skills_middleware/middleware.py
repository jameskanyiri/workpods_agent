import os

from langchain.agents.middleware.types import (
    AgentMiddleware,
    ContextT,
    ModelRequest,
)
from langchain_core.messages import SystemMessage
from typing_extensions import override

from src.middleware.skills_middleware.state import SkillsState
from src.middleware.skills_middleware.schema import SkillMetadata
from src.middleware.skills_middleware.registry import discover_skills
from src.middleware.skills_middleware.prompt import SKILLS_SYSTEM_PROMPT


# Default skills directory: src/skills/
DEFAULT_SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "skills")


class SkillsMiddleware(
    AgentMiddleware[SkillsState, ContextT]
):
    """Middleware for discovering and exposing agent skills.

    Scans a skills directory for SKILL.md files, parses their frontmatter,
    and injects a skills listing into the system prompt.

    Uses progressive disclosure: the agent sees skill names and descriptions
    in the system prompt, and reads full instructions via read_file when needed.
    No activate_skill tool — the agent uses read_file directly.
    """

    state_schema = SkillsState

    def __init__(self, skills_dir: str | None = None) -> None:
        super().__init__()
        self._skills_dir = os.path.abspath(skills_dir or DEFAULT_SKILLS_DIR)
        self._skills: list[SkillMetadata] = discover_skills(self._skills_dir)

    def _format_skills_list(self) -> str:
        """Format discovered skills as a bullet list."""
        if not self._skills:
            return "(No skills available)"

        lines = []
        for s in self._skills:
            lines.append(f"- **`{s['name']}`**: {s['description']}")
            lines.append(f"  - Read `{s['path']}` for full instructions")
        return "\n".join(lines)

    def _build_system_prompt(self, request: ModelRequest) -> ModelRequest:
        """Inject skills listing into the system prompt."""

        skills_prompt = SKILLS_SYSTEM_PROMPT.format(
            skills_location=f"Skills directory: `{self._skills_dir}`",
            skills_list=self._format_skills_list(),
        )

        extra = {"type": "text", "text": skills_prompt}

        if request.system_message is not None:
            new_content = [*request.system_message.content_blocks, extra]
        else:
            new_content = [extra]

        return request.override(system_message=SystemMessage(content=new_content))

    async def awrap_model_call(self, request, handler):
        return await handler(self._build_system_prompt(request))

    @override
    async def abefore_agent(self, state, runtime):
        """Load skills metadata into state on first turn."""
        if "skills_metadata" in state:
            return None
        return {"skills_metadata": self._skills}
