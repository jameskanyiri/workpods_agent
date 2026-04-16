WRITE_TODOS_SYSTEM_PROMPT = """
## `write_todos` — Planning Tool

You have access to the `write_todos` tool for planning and tracking multi-step work.

### Precondition
- If the user's request matches an available skill, read that skill's `SKILL.md` with `read_file` before calling `write_todos`.
- `write_todos` is for planning execution after you understand the applicable skill workflow.

### When You MUST Use It
- **Any task requiring 3+ tool calls** — call `write_todos` BEFORE your first `api_request`.
- **Skill workflows** — project setup, task breakdown, milestone creation, bulk operations.
- **Multi-resource operations** — creating a project with milestones and tasks, bulk status updates.

### When to Skip It
- Single lookups: "list my projects", "what tasks are due?"
- Quick updates: "mark this task done", "change priority to high"
- Any task that needs only 1-2 tool calls.

### How to Use It
1. If a matching skill exists, read it first.
2. Call `write_todos` with your full plan BEFORE executing any steps.
3. Set the first step to `in_progress` immediately.
4. After completing each step, call `write_todos` again to mark it `completed` and set the next step to `in_progress`.
5. Do NOT batch multiple steps before marking them as completed.
6. Revise the plan as you learn new information.

### Rules
- Never call `write_todos` multiple times in parallel.
- Always start your plan with "Resolve workspace" if workspace_id is not yet known.
- Include a "Confirm with user" step before executing destructive or multi-resource operations.
- Do not use `write_todos` as a shortcut to skip reading a matching skill."""  # noqa: E501
