SUMMARY_GENERATION_PROMPT = """\
You are a context extraction assistant. Your job is to compress a conversation \
history into the most important information so the agent can continue working \
without losing track of what happened.

Structure your summary with these sections:

## SESSION INTENT
What is the user's primary goal? What overall task is being accomplished?

## KEY DECISIONS & PROGRESS
- Important choices made and why
- What was completed successfully
- What failed and what was learned

## ARTIFACTS
Files created, modified, or read. API calls made and their outcomes. \
Include specific paths and endpoint URLs.

## CURRENT STATE
Where things stand right now — what's done and what's in progress.

## NEXT STEPS
What specific tasks remain? What should the agent do next?

---

Respond ONLY with the structured summary. Be concise but don't lose critical details \
like file paths, endpoint URLs, error messages, or user preferences.

<messages>
{messages}
</messages>
"""


COMPACT_TOOL_PROMPT = """\
## Compact Conversation Tool `compact_conversation`

You have access to a `compact_conversation` tool that compresses your conversation \
history to free up context space.

Use it when:
- The user asks to move on to a completely new task
- You've finished a large task and the working context is no longer needed
- You notice your responses are getting slower or less coherent

The tool preserves your most recent messages and generates a summary of older ones. \
The full history is saved to the filesystem if you need to look back.
"""


HISTORY_OFFLOAD_NOTICE = """\
[Conversation history was compacted. {msg_count} older messages were summarized \
and the full history was saved to {file_path}. Use `read_file` to review if needed.]

{summary}
"""

HISTORY_OFFLOAD_NOTICE_NO_FILE = """\
[Conversation history was compacted. {msg_count} older messages were summarized.]

{summary}
"""
