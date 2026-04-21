from dataclasses import dataclass, field


@dataclass
class SubAgentConfig:
    name: str
    description: str
    system_prompt: str
    tools: list = field(default_factory=list)
    model: str | None = None  # None = inherit from main agent context
    state_schema: type | None = None  # None = use default SubAgentState
    middleware: list = field(default_factory=list)
    # Middlewares that should wrap the subagent. Middlewares contribute their
    # own tools and system-prompt injections, so subagents that opt into a
    # middleware stack get the same capabilities as the main agent without
    # having to list every tool explicitly.
    context_schema: type | None = None
    # Required when any middleware reads from runtime.context (e.g. auth,
    # dynamic model selection). Usually the same schema as the main agent.


# Registry populated by subagent modules
SUBAGENT_REGISTRY: dict[str, SubAgentConfig] = {}


def register_subagent(config: SubAgentConfig) -> None:
    """Register a subagent config in the global registry."""
    SUBAGENT_REGISTRY[config.name] = config
