"""Pre-completion check middleware — forces a verification pass before the agent exits.

When the agent produces an AI message with no tool calls (i.e. it wants to
stop), this middleware intercepts and redirects back to the model with a
verification prompt. This is the "Ralph Wiggum" pattern: the agent thinks
it's done, but a hook forces one more pass to self-verify against the
original task.

The middleware tracks a counter so it only forces **one** verification pass,
preventing infinite loops.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain.agents.middleware.types import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from src.middleware.pre_completion_check.state import PreCompletionCheckState
from src.middleware.pre_completion_check.prompt import VERIFICATION_PROMPT

logger = logging.getLogger(__name__)


class PreCompletionCheckMiddleware(AgentMiddleware[PreCompletionCheckState]):
    """Intercepts agent completion to force a self-verification pass.

    Uses the ``aafter_model`` hook with ``can_jump_to=["model"]`` to redirect
    the agent back to the model node when it tries to finish without having
    verified its work.

    The verification pass runs at most once per agent invocation, controlled
    by the ``_completion_check_count`` state counter.
    """

    state_schema = PreCompletionCheckState

    def __init__(self, max_checks: int = 1) -> None:
        super().__init__()
        self._max_checks = max_checks

    def _is_completion_attempt(self, state: PreCompletionCheckState) -> bool:
        """Check if the last AI message has no tool calls (agent wants to stop)."""
        messages = state.get("messages", [])
        if not messages:
            return False

        last_ai = next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)),
            None,
        )
        if last_ai is None:
            return False

        # Agent is completing if it has no tool calls
        return not last_ai.tool_calls

    def _has_user_message(self, state: PreCompletionCheckState) -> bool:
        """Check that there's at least one human message (a real task to verify against)."""
        messages = state.get("messages", [])
        return any(isinstance(m, HumanMessage) for m in messages)

    @hook_config(can_jump_to=["model"])
    async def aafter_model(
        self, state: PreCompletionCheckState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """If the agent is completing, force a verification pass (once)."""
        if not self._is_completion_attempt(state):
            return None

        check_count = state.get("_completion_check_count", 0)
        if check_count >= self._max_checks:
            return None

        # Don't force verification on trivial interactions (no real task)
        if not self._has_user_message(state):
            return None

        logger.info(
            "[pre_completion_check] Agent attempting to complete — forcing verification pass %d/%d",
            check_count + 1,
            self._max_checks,
        )

        return {
            "_completion_check_count": check_count + 1,
            "messages": [
                SystemMessage(content=VERIFICATION_PROMPT),
            ],
            "jump_to": "model",
        }
