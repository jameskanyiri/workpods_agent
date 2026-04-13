TODO_TOOL_DESCRIPTION = """Create and manage a structured, ordered task list. Replaces the entire list on every call — always pass the full list.

RULES — follow all of these:
- Always plan before executing. Never jump into multi-step work without a todo list.
- Set the first task to in_progress immediately. Never create a plan with all tasks pending.
- Every task needs a description. Not just a label — a full description of what the task involves, what inputs it needs, and what output it produces.
- Break work into discrete, verifiable steps. Each task should have a single clear success condition.
- Front-load information gathering. The first 1–2 tasks are almost always: load skill (if relevant), then explore workspace / read relevant files.
- Never generate documents before prerequisites are complete. Analysis before synthesis. Always.
- Only one task should be in_progress at a time.
- Always pass the full list — partial updates will overwrite existing tasks.
- NEVER leave description empty.

Task structure:
- id: unique string ("1", "2", ...)
- label: 5–8 words. Short display title. E.g., "Activate payroll skill", "Read existing ledger data"
- status: in_progress for the current task, pending for future tasks, completed for done tasks.
- description: Full breakdown — what this task does, what it needs as input, what it produces as output. When completed, update with what was actually found or done.

Description by status:
- pending: What this task involves, what inputs are needed, what the expected output is.
- in_progress: Same as pending, plus any findings or decisions made so far.
- completed: What was actually done, key decisions made, files created or modified.

When to update the plan:
- After every completed task, update that task to completed and set the next task to in_progress in the same call (saves a tool call).
- If a completed task reveals new information that changes the plan, add, remove, or reorder tasks before continuing. The plan is a living document — update it as you learn.

display_name: Reflect the action in plain language. E.g., "Planning tasks", "Starting site analysis", "Completed executive summary". NEVER use file names or extensions. Default: "Updating tasks".
"""