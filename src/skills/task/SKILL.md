---
name: task
description: Triggered when the user wants to create, break down, assign, prioritize, label, schedule, update, or review tasks, including starter task sets, bulk task changes, milestone linkage, and "what should happen next" at the task level. Do not use this as the first skill when the real problem is commercial triage, renewal strategy, or account prioritization.
---

# Task Skill

## Purpose

Own task creation, task decomposition, task updates, assignment, due dates, priorities, labels, and task linkage to milestones. This skill operationalizes a chosen next move. It does not own project-level communication objects except when it needs to suggest a handoff to comments, updates, or threads, and it should not invent task work before the business bottleneck is clear.

Common incoming handoffs:
- `project` when the next move becomes actionable task work
- `commercial-lifecycle` after the business bottleneck is identified
- `milestone` when a phase already exists and now needs tasks

Common outgoing handoffs:
- `milestone` when the user is really defining a phase or checkpoint
- `comments` for short task-level notes
- `project-updates` for project-level summaries
- `persistent-files` for durable task documents

## Trigger Signals

Use this skill when the user says things like:
- "create tasks"
- "break this down"
- "assign this task"
- "mark it done"
- "what tasks are due"
- "what should I work on next"
- "attach this to the milestone"

Prefer `commercial-lifecycle` first when the user is really asking:
- which account matters most
- how to improve sales
- how to prevent expiry
- which clients are worth renewing or reactivating

## Workflow

1. Resolve workspace and project.
2. Read:
   - task statuses
   - members when assignment matters
   - labels when categorization matters
   - project detail or task list when checking duplicates or milestone linkage
3. Decide the operating mode:
   - direct action for simple task CRUD, assignment, status, due date, label, or milestone-link changes
   - draft-first for bulk task plans, weekly assignment plans, or complex multi-task decomposition needing review
   - document-only for task-scoped long-form execution briefs or troubleshooting notes
4. Maintain `/.workpods-agent/projects/<project-slug>/task-breakdown.md` when the work needs decomposition or a reusable draft.
5. For multi-step work, create todos before writes.
6. Break broad work into atomic tasks with one owner and a realistic due date path.
7. Confirm before bulk creation or bulk updates.
8. Execute task writes, then assignee and label sub-resource writes if needed.
9. Verify task state when the user cares about milestone linkage, assignee, priority, due date, or labels.

## Decision Rules

- If a task title naturally contains "and", consider splitting it.
- Search for duplicates before creating tasks from a high-level goal.
- If the user describes a phase, checkpoint, or major stage, recommend a milestone before creating many tasks.
- If the business bottleneck is not yet clear, do not create tasks. Identify whether the issue is qualification, follow-up, renewal, billing, service continuity, or ownership first.
- Default to actionable titles and realistic due dates.
- If the user is asking for a simple task update, apply it directly instead of creating a task document.
- Use a task document only when the task needs substantial long-form guidance that would be too heavy for a task comment.
- If the task document should be durable and reusable, read `persistent-files` and save it into the backend files API under the `task` home.
- If the next action becomes a phase decision, project-level communication, or durable document persistence, hand off to the owning skill before proceeding.
- Prefer the seeded task-label vocabulary when it fits the work, especially `site-assessment`, `follow-up`, `mc-renewal`, `warranty`, `maintenance`, `billing`, `reporting`, `service-check`, `spot-check`, `review`, `documentation`, and `on-call`.
- For `PROPOSAL SENT`, default task direction toward follow-up and close planning.
- For `UNDER WAR`, default task direction toward warranty follow-up and MC conversion preparation.
- For `CURRENT MC`, default task direction toward renewal prevention, billing visibility, and service continuity.
- If blocked, identify the next unblocked task or the missing dependency.

## Gotchas

- Task writes often require follow-up sub-resource writes for assignees and labels.
- Status ids must come from workspace task statuses.
- Broad tasks create hidden work and poor tracking.
- Generic admin tasks are usually weaker than business-motion tasks with the correct label and owner.
- Milestone linkage should be verified when it matters to the workflow.
- Do not create a task document when a task comment or direct task update is the right object.

## Scratchpad Contract

- Maintain `/.workpods-agent/projects/<project-slug>/task-breakdown.md`.
- Save task-scoped long-form documents under `/.workpods-agent/projects/<project-slug>/tasks/<task-slug>/` when the workflow is document-only or draft-first.
- Record:
  - task goal
  - decomposition
  - dependencies
  - intended owners
  - due date logic
  - milestone linkage

## References Map

- Read `references/api.md` for create/update/list/assignee/label/comment routes.
- Read `references/workflows.md` for breakdown, duplicate check, and bulk change flow.
- Read `references/gotchas.md` before creating starter task sets or doing bulk updates.
- Read `../persistent-files/SKILL.md` when the task workflow needs a durable backend file.
- Read `examples/breakdown.md` for a starter-task flow.
- Use `templates/task-breakdown.md` when updating the scratchpad.

## Completion Criteria

- Tasks are created or updated as requested, or the blocker is explicit.
- Duplicate risk has been handled for creation flows.
- Required assignee, priority, milestone, and label context is applied or clearly noted.
- The task breakdown scratchpad reflects the current execution plan and the tasks map to a real operating motion.
