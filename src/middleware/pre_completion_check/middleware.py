"""Pre-completion check middleware — forces a verification pass before the agent exits.

When the agent produces an AI message with no tool calls (i.e. it wants to
stop), this middleware intercepts and redirects back to the model with a
verification prompt injected into the system message for one call. If the
model revises its answer, the original "I'm done" attempt is removed from
state so nothing about the verification flow leaks to the UI.

The middleware tracks a counter so it forces at most ``max_checks``
verification passes per invocation, preventing infinite loops.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain.agents.middleware.types import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from src.middleware.pre_completion_check.state import PreCompletionCheckState
from src.middleware.pre_completion_check.prompt import VERIFICATION_PROMPT

logger = logging.getLogger(__name__)


class PreCompletionCheckMiddleware(AgentMiddleware[PreCompletionCheckState]):
    """Intercepts agent completion to force a self-verification pass.

    Flow:
    - ``aafter_model`` detects a completion attempt (AI message with no tool
      calls) and sets ``_needs_verification=True`` + records the message ID.
      It then jumps back to the model without writing anything to the message
      history.
    - ``awrap_model_call`` sees the flag on the next call and appends the
      verification prompt to the system message for that single call only.
    - ``aafter_model`` runs again on the revised response; it removes the
      original "I'm done" AI message from state via ``RemoveMessage`` so the
      UI only ever sees the corrected final answer.

    The verification prompt is never added to ``state['messages']``; it lives
    only in the outgoing system prompt for one call and is then gone. The
    premature AI message is stripped before the UI can render a final frame
    containing it.
    """

    state_schema = PreCompletionCheckState

    def __init__(self, max_checks: int = 3) -> None:
        super().__init__()
        self._max_checks = max_checks

    def before_agent(
        self, state: PreCompletionCheckState, runtime: Runtime, config: RunnableConfig
    ) -> dict[str, Any] | None:
        """Reset verification state at the start of each run.

        Without this, the counter and flags persist in checkpointed state
        across runs within the same thread. This also covers the "user pushes
        back" case — each new user turn is a new invocation, so state zeroes
        automatically before the next verification can fire.
        """
        updates: dict[str, Any] = {}
        if state.get("_completion_check_count", 0) > 0:
            updates["_completion_check_count"] = 0
        if state.get("_needs_verification", False):
            updates["_needs_verification"] = False
        if state.get("_completion_message_id"):
            updates["_completion_message_id"] = ""
        return updates or None

    async def abefore_agent(
        self, state: PreCompletionCheckState, runtime: Runtime, config: RunnableConfig
    ) -> dict[str, Any] | None:
        """Async variant of before_agent."""
        return self.before_agent(state, runtime, config)

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

        return not last_ai.tool_calls

    def _last_ai_message(self, state: PreCompletionCheckState) -> AIMessage | None:
        messages = state.get("messages", [])
        return next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)),
            None,
        )

    def _has_user_message(self, state: PreCompletionCheckState) -> bool:
        """Check that there's at least one human message (a real task to verify against)."""
        messages = state.get("messages", [])
        return any(isinstance(m, HumanMessage) for m in messages)

    async def awrap_model_call(self, request: Any, handler: Any) -> Any:
        """Inject the verification prompt when a verification pass is pending.

        The prompt is appended to the system message for this single model
        call. It is never written to ``state['messages']``, so it cannot leak
        to the UI.
        """
        needs_verification = request.state.get("_needs_verification", False)
        if not needs_verification:
            return await handler(request)

        extra = {"type": "text", "text": VERIFICATION_PROMPT}
        if request.system_message is not None:
            new_content = [*request.system_message.content_blocks, extra]
        else:
            new_content = [extra]

        request = request.override(system_message=SystemMessage(content=new_content))
        return await handler(request)

    @hook_config(can_jump_to=["model"])
    async def aafter_model(
        self, state: PreCompletionCheckState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Two-phase hook: clean up from the prior verification, then decide
        whether to schedule another one."""
        updates: dict[str, Any] = {}

        # Phase A — cleanup after a verification cycle finished.
        if state.get("_needs_verification", False):
            updates["_needs_verification"] = False
            premature_id = state.get("_completion_message_id", "") or ""
            if premature_id:
                updates["messages"] = [RemoveMessage(id=premature_id)]
                updates["_completion_message_id"] = ""

        # Phase B — is the current AI message another completion attempt?
        if not self._is_completion_attempt(state):
            return updates or None

        check_count = state.get("_completion_check_count", 0)
        if check_count >= self._max_checks:
            return updates or None

        if not self._has_user_message(state):
            return updates or None

        last_ai = self._last_ai_message(state)
        completion_message_id = getattr(last_ai, "id", "") or ""

        logger.info(
            "[pre_completion_check] Agent attempting to complete — forcing verification pass %d/%d",
            check_count + 1,
            self._max_checks,
        )

        updates["_completion_check_count"] = check_count + 1
        updates["_needs_verification"] = True
        updates["_completion_message_id"] = completion_message_id
        updates["jump_to"] = "model"
        return updates
