"""Loop detection middleware — nudges the agent when it repeats the same action too many times.

Tracks per-file edit counts and per-endpoint API call counts. When any count
exceeds a threshold, injects an advisory warning into the system prompt
encouraging the agent to step back and reconsider its approach.

This does NOT block the agent — it only adds context. The agent can continue
if it genuinely needs more edits.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain.agents.middleware.types import AgentMiddleware, ContextT, ModelRequest
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.runtime import Runtime

from src.middleware.loop_detection.state import LoopDetectionState

logger = logging.getLogger(__name__)

# Tool names we track for loop detection
_TRACKED_TOOLS = {
    "edit_file": lambda args: args.get("file_path", "unknown"),
    "api_request": lambda args: f'{args.get("method", "GET")} {args.get("endpoint", "/")}',
}

_WARNING_TEMPLATE = (
    "## Loop Detection Warning\n\n"
    "You have repeated the following actions multiple times:\n\n"
    "{items}\n\n"
    "Consider stepping back and reconsidering your approach rather than "
    "making incremental fixes to the same target. Common recovery strategies:\n"
    "- Re-read the original requirement\n"
    "- Read the full file to understand the broader context\n"
    "- Try a different approach entirely\n"
    "- Ask the user for clarification if you're stuck\n"
)


class LoopDetectionMiddleware(AgentMiddleware[LoopDetectionState, ContextT]):
    """Tracks repeated tool call patterns and injects advisory warnings.

    Uses ``aafter_model`` to update counts after every model response, and
    ``awrap_model_call`` to inject any pending warnings into the system prompt.

    Args:
        threshold: Number of repetitions before injecting a warning.
            Defaults to 5.
    """

    state_schema = LoopDetectionState

    def __init__(self, threshold: int = 5) -> None:
        super().__init__()
        self._threshold = threshold

    async def aafter_model(
        self, state: LoopDetectionState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Update tool call counts based on the latest AI message."""
        messages = state.get("messages", [])
        if not messages:
            return None

        last_ai = next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)),
            None,
        )
        if last_ai is None or not last_ai.tool_calls:
            return None

        counts = dict(state.get("_tool_call_counts", {}))
        changed = False

        for tc in last_ai.tool_calls:
            tool_name = tc.get("name", "")
            key_fn = _TRACKED_TOOLS.get(tool_name)
            if key_fn is None:
                continue

            args = tc.get("args", {})
            target = key_fn(args)
            key = f"{tool_name}:{target}"
            counts[key] = counts.get(key, 0) + 1
            changed = True

        if not changed:
            return None

        # Build warnings for any counts exceeding threshold
        warnings: list[str] = []
        for key, count in counts.items():
            if count >= self._threshold and count % self._threshold == 0:
                tool_name, target = key.split(":", 1)
                warnings.append(f"- `{tool_name}` on `{target}`: **{count} times**")
                logger.warning(
                    "[loop_detection] %s called %d times on %s",
                    tool_name,
                    count,
                    target,
                )

        updates: dict[str, Any] = {"_tool_call_counts": counts}
        if warnings:
            updates["_loop_warnings"] = warnings

        return updates

    async def awrap_model_call(
        self, request: ModelRequest, handler: Any
    ) -> Any:
        """Inject any pending loop warnings into the system prompt."""
        warnings = request.state.get("_loop_warnings", [])

        if warnings:
            warning_text = _WARNING_TEMPLATE.format(items="\n".join(warnings))
            extra = {"type": "text", "text": warning_text}

            if request.system_message is not None:
                new_content = [*request.system_message.content_blocks, extra]
            else:
                new_content = [extra]

            request = request.override(
                system_message=SystemMessage(content=new_content)
            )

        return await handler(request)
