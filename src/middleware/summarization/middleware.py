"""Custom summarization middleware for conversation compaction.

When the conversation grows too long (measured by token count or message count),
this middleware:

1. Partitions messages into old (to summarize) and recent (to keep)
2. Offloads the full old messages to a VFS file for later retrieval
3. Calls a fast LLM to generate a structured summary
4. Replaces the old messages with the summary in state

This keeps the agent's context window manageable during long sessions while
preserving the ability to look back at full history via read_file.

## How it works

The middleware uses `abefore_model` — it runs before every model call, checks
if the conversation exceeds the threshold, and if so, compacts it by:
- Counting tokens across all messages
- If over the trigger threshold, finding a safe cutoff point
- Generating a summary of everything before the cutoff
- Saving the full evicted messages to `/conversation_history/{thread_id}.md`
- Replacing old messages with a single HumanMessage containing the summary

## Configuration

- `trigger`: When to fire — ("tokens", N), ("messages", N), or ("fraction", 0.0-1.0)
- `keep`: How much recent context to preserve after compaction
- `summary_model`: Which LLM to use for generating summaries (use a fast/cheap one)
- `max_input_tokens`: Context window size (used with fraction-based triggers)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from langchain.agents.middleware.types import AgentMiddleware, ContextT
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
    ToolMessage,
    get_buffer_string,
)
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.runtime import Runtime

from src.middleware.summarization.state import SummarizationEvent, SummarizationState
from src.middleware.summarization.prompt import (
    SUMMARY_GENERATION_PROMPT,
    HISTORY_OFFLOAD_NOTICE,
    HISTORY_OFFLOAD_NOTICE_NO_FILE,
)

logger = logging.getLogger(__name__)

# Sentinel used by LangGraph to remove all messages from state
REMOVE_ALL_MESSAGES = "__remove_all__"

# ─── Types ───────────────────────────────────────────────────────────

# ContextSize can be:
#   ("tokens", 100000)   - absolute token count
#   ("messages", 40)     - absolute message count
#   ("fraction", 0.85)   - fraction of max_input_tokens
ContextSize = tuple[str, int | float]


class SummarizationMiddleware(AgentMiddleware[SummarizationState, ContextT]):
    """Automatically compacts conversations when they exceed a size threshold.

    Args:
        summary_model: LLM for generating summaries. Use a fast/cheap model
            (e.g. "openai:gpt-4.1-mini"). Can be a string or BaseChatModel.
        trigger: When to fire summarization. Defaults to ("tokens", 120000).
        keep: How many recent messages/tokens to preserve. Defaults to ("messages", 10).
        max_input_tokens: Total context window size. Required for fraction-based triggers.
        summary_prompt: Custom prompt template for summary generation.
            Must contain {messages} placeholder.
    """

    state_schema = SummarizationState

    def __init__(
        self,
        summary_model: str | BaseChatModel = "openai:gpt-4.1-mini",
        *,
        trigger: ContextSize = ("tokens", 120_000),
        keep: ContextSize = ("messages", 10),
        max_input_tokens: int = 200_000,
        summary_prompt: str | None = None,
    ) -> None:
        super().__init__()

        # Defer model init until first use (avoids needing API keys at import time)
        self._model: BaseChatModel | None = None
        self._model_spec = summary_model

        self._trigger = trigger
        self._keep = keep
        self._max_input_tokens = max_input_tokens
        self._summary_prompt = summary_prompt or SUMMARY_GENERATION_PROMPT

    def _get_model(self) -> BaseChatModel:
        """Lazily initialize the summary model on first use."""
        if self._model is None:
            if isinstance(self._model_spec, str):
                self._model = init_chat_model(self._model_spec)
            else:
                self._model = self._model_spec
        return self._model

    # ─── Trigger detection ───────────────────────────────────────────

    def _count_tokens(self, messages: list[AnyMessage]) -> int:
        """Count tokens across all messages."""
        try:
            return count_tokens_approximately(messages)
        except Exception:
            # Fallback: rough estimate at 4 chars per token
            total_chars = sum(len(str(m.content)) for m in messages)
            return total_chars // 4

    def _should_summarize(self, messages: list[AnyMessage], total_tokens: int) -> bool:
        """Check if the conversation exceeds the trigger threshold."""
        kind, value = self._trigger

        if kind == "tokens":
            return total_tokens >= int(value)
        elif kind == "messages":
            return len(messages) >= int(value)
        elif kind == "fraction":
            return total_tokens >= int(self._max_input_tokens * float(value))

        return False

    # ─── Cutoff calculation ──────────────────────────────────────────

    def _determine_cutoff_index(self, messages: list[AnyMessage]) -> int:
        """Find the index that splits messages into [to_summarize | to_keep].

        Returns the cutoff index — everything before it gets summarized,
        everything from it onward is preserved.
        """
        kind, value = self._keep

        if kind == "messages":
            keep_count = int(value)
            cutoff = max(0, len(messages) - keep_count)
        elif kind == "tokens":
            # Walk backwards from the end, accumulating tokens until we hit the limit
            keep_tokens = int(value)
            accumulated = 0
            cutoff = len(messages)
            for i in range(len(messages) - 1, -1, -1):
                msg_tokens = self._count_tokens([messages[i]])
                if accumulated + msg_tokens > keep_tokens:
                    break
                accumulated += msg_tokens
                cutoff = i
        elif kind == "fraction":
            keep_tokens = int(self._max_input_tokens * float(value))
            accumulated = 0
            cutoff = len(messages)
            for i in range(len(messages) - 1, -1, -1):
                msg_tokens = self._count_tokens([messages[i]])
                if accumulated + msg_tokens > keep_tokens:
                    break
                accumulated += msg_tokens
                cutoff = i
        else:
            cutoff = max(0, len(messages) - 10)

        # Find a safe cutoff point — don't split in the middle of a
        # tool-call / tool-result pair
        cutoff = self._find_safe_cutoff(messages, cutoff)

        return cutoff

    def _find_safe_cutoff(self, messages: list[AnyMessage], cutoff: int) -> int:
        """Adjust cutoff so we don't orphan a ToolMessage from its AIMessage.

        If the message at cutoff is a ToolMessage, walk forward until we're
        past all ToolMessages in the same group.
        """
        while cutoff < len(messages) and isinstance(messages[cutoff], ToolMessage):
            cutoff += 1

        # Also don't cut right after an AIMessage with tool_calls — the
        # ToolMessages that follow it need to stay with it
        if cutoff > 0 and cutoff < len(messages):
            prev = messages[cutoff - 1]
            if isinstance(prev, AIMessage) and prev.tool_calls:
                # Walk forward past all the ToolMessages for this AI message
                while cutoff < len(messages) and isinstance(messages[cutoff], ToolMessage):
                    cutoff += 1

        return cutoff

    # ─── Summary generation ──────────────────────────────────────────

    async def _generate_summary(self, messages: list[AnyMessage]) -> str:
        """Call the summary model to compress messages into a structured summary."""
        # Format messages into readable text
        messages_text = get_buffer_string(messages)

        # Trim if too long for the summary model (keep ~4000 tokens worth)
        max_chars = 16_000
        if len(messages_text) > max_chars:
            # Keep the beginning and end
            half = max_chars // 2
            messages_text = (
                messages_text[:half]
                + f"\n\n... [{len(messages_text) - max_chars} characters omitted] ...\n\n"
                + messages_text[-half:]
            )

        prompt = self._summary_prompt.format(messages=messages_text)

        try:
            model = self._get_model()
            response = await model.ainvoke([HumanMessage(content=prompt)])
            return str(response.content)
        except Exception as exc:
            logger.error("[summarization] Summary generation failed: %s", exc)
            # Fallback: simple truncation
            return f"[Summary generation failed. {len(messages)} messages were compacted.]\n\n{messages_text[:2000]}..."

    # ─── VFS offloading ──────────────────────────────────────────────

    def _format_messages_for_offload(self, messages: list[AnyMessage]) -> str:
        """Format messages as markdown for storage in VFS."""
        lines = [
            f"# Conversation History (offloaded {datetime.now(UTC).isoformat()})",
            f"Messages: {len(messages)}",
            "",
            "---",
            "",
        ]

        for msg in messages:
            role = type(msg).__name__.replace("Message", "")
            content = str(msg.content) if isinstance(msg.content, str) else str(msg.content)

            lines.append(f"### {role}")

            # Show tool calls on AI messages
            if isinstance(msg, AIMessage) and msg.tool_calls:
                tool_names = [tc.get("name", "?") for tc in msg.tool_calls]
                lines.append(f"*Tool calls: {', '.join(tool_names)}*")

            # Show tool call ID on tool messages
            if isinstance(msg, ToolMessage):
                lines.append(f"*Tool call ID: {msg.tool_call_id}*")

            # Truncate very long content for the offload file
            if len(content) > 5000:
                content = content[:5000] + f"\n\n... [{len(content) - 5000} chars truncated]"

            lines.append(content)
            lines.append("")

        return "\n".join(lines)

    def _get_history_path(self, runtime: Runtime) -> str:
        """Build VFS path for offloaded conversation history."""
        # Try to get thread_id from langgraph config
        thread_id = "unknown"
        try:
            config = getattr(runtime, "config", None)
            if config and isinstance(config, dict):
                thread_id = config.get("configurable", {}).get("thread_id", "unknown")
        except Exception:
            pass

        if thread_id == "unknown":
            thread_id = uuid.uuid4().hex[:12]

        return f"/conversation_history/{thread_id}.md"

    # ─── Main hook ───────────────────────────────────────────────────

    async def abefore_model(
        self, state: SummarizationState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Check conversation size and compact if threshold is exceeded.

        This runs before every model call. If the conversation is within
        limits, it returns None (no-op). If it exceeds the trigger, it:
        1. Partitions messages into old and recent
        2. Generates a summary of old messages
        3. Offloads full old messages to VFS
        4. Replaces all messages with [summary, ...recent]
        """
        messages: list[AnyMessage] = state.get("messages", [])
        if len(messages) < 3:
            return None

        total_tokens = self._count_tokens(messages)

        if not self._should_summarize(messages, total_tokens):
            return None

        cutoff = self._determine_cutoff_index(messages)
        if cutoff <= 0:
            return None

        messages_to_summarize = messages[:cutoff]
        preserved_messages = messages[cutoff:]

        logger.info(
            "[summarization] Compacting: %d messages (%d tokens) → summarizing %d, keeping %d",
            len(messages),
            total_tokens,
            len(messages_to_summarize),
            len(preserved_messages),
        )

        # Generate summary
        summary_text = await self._generate_summary(messages_to_summarize)

        # Offload full history to VFS
        history_path = self._get_history_path(runtime)
        offload_content = self._format_messages_for_offload(messages_to_summarize)
        file_update: dict[str, Any] | None = None

        try:
            file_update = {
                history_path: {
                    "content": offload_content,
                    "encoding": "utf-8",
                }
            }
            logger.info("[summarization] Offloaded %d messages to %s", len(messages_to_summarize), history_path)
        except Exception as exc:
            logger.error("[summarization] Failed to offload history: %s", exc)
            history_path = None

        # Build the summary message
        if history_path:
            notice = HISTORY_OFFLOAD_NOTICE.format(
                msg_count=len(messages_to_summarize),
                file_path=history_path,
                summary=summary_text,
            )
        else:
            notice = HISTORY_OFFLOAD_NOTICE_NO_FILE.format(
                msg_count=len(messages_to_summarize),
                summary=summary_text,
            )

        summary_message = HumanMessage(
            content=notice,
            id=str(uuid.uuid4()),
        )

        # Track summarization event
        event: SummarizationEvent = {
            "cutoff_index": cutoff,
            "summary_text": summary_text,
            "history_path": history_path,
        }

        total_summarizations = state.get("_total_summarizations", 0) + 1

        # Build state update: remove all old messages, replace with summary + preserved
        updates: dict[str, Any] = {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                summary_message,
                *preserved_messages,
            ],
            "_summarization_event": event,
            "_total_summarizations": total_summarizations,
        }

        if file_update:
            updates["files"] = file_update

        logger.info(
            "[summarization] Compaction #%d complete. Summary: %d chars, preserved: %d messages",
            total_summarizations,
            len(summary_text),
            len(preserved_messages),
        )

        return updates
