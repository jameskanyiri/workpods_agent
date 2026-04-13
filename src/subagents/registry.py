from dataclasses import dataclass, field


@dataclass
class SubAgentConfig:
    name: str
    description: str
    system_prompt: str
    tools: list = field(default_factory=list)
    model: str | None = None  # None = inherit from main agent context
    state_schema: type | None = None  # None = use default SubAgentState


# Registry populated by subagent modules
SUBAGENT_REGISTRY: dict[str, SubAgentConfig] = {}


def register_subagent(config: SubAgentConfig) -> None:
    """Register a subagent config in the global registry."""
    SUBAGENT_REGISTRY[config.name] = config
