TASK_TOOL_DESCRIPTION = """
    Delegate a self-contained task to a specialized subagent that works in an isolated context.
    The subagent executes independently and writes its output to VFS. You can call this tool
    multiple times in parallel — each call runs in its own context window.

    Available agents:
    - "writer": Writes a single document section given a brief and data context.
    - "researcher": Researches a topic using web search (Tavily) and produces a sourced summary.
    - "general": General-purpose agent for complex, multi-step tasks. Has access to the full
      workspace (VFS), skill files, and can run scripts. Use for creating detailed plans,
      large analysis work, multi-step data processing, workspace organization, or any heavy
      task that would bloat your context. Do NOT use for simple single-step operations.

    IMPORTANT:
    - Always provide a unique output_path for each parallel call to avoid file collisions.
    - Include all relevant data in context_data — the subagent has no access to your conversation history.
    - Use "writer" and "researcher" during document generation to write sections or gather data in parallel.
    - Use "general" for complex tasks that require many tool calls — it keeps your context clean.

    Args:
        agent_name: The subagent to invoke. Must be a registered agent name (e.g., "writer", "researcher", "general").
        description: Detailed brief of what the subagent should produce. Include section title,
                     scope, tone, language, and any specific instructions.
        context_data: Paste relevant data the subagent needs (e.g., site data, analysis results).
                      The subagent only sees this — not your full conversation.
        output_path: VFS path where the subagent should write its output (e.g., "/sections/03-revenue-analysis.md").
        display_name: Short label for the UI. E.g., "Writing revenue analysis section".
    """
