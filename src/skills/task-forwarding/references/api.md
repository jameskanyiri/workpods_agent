# Task Forwarding API Reference

This skill is **diagnostic-and-orchestration-heavy**. It identifies blockers and the next unblocked move on a task or workstream, then hands off to the owning skill for any actual write. Read this file for *how* to read state and *what* to look for; read the owning sub-skill's `references/api.md` before any write.

## Owning sub-skills (read these for field schemas before writing)

- `task/references/api.md`               — task fields, status changes, assignees, labels, due dates, milestone linkage, reorder
- `milestone/references/api.md`          — milestone state for phase context
- `project/references/api.md`            — project-level fields (lead, members, status)
- `comments/references/api.md`           — short blocker / handoff notes on a task
- `project-updates/references/api.md`    — escalation to a project-level checkpoint when the blocker matters beyond the task
- `labels/references/api.md`             — applying or filtering by labels (e.g., `blocked`, `waiting`)
- `workspace/references/api.md`          — member lookup for reassignment

## Endpoints used by the diagnosis

The reads that drive blocker analysis, in approximate order:

1. `GET /v1/workspaces/default`                                            — resolve workspace if missing
2. `GET /v1/workspaces/{workspace_id}/projects/{project_id}`               — full project state (embeds up to 200 tasks + milestones + task statuses)
3. `GET /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}` — focused task read (assignees, labels, due_date, milestone_id, thread_id)
4. `GET /v1/workspaces/{workspace_id}/projects/{project_id}/tasks?status_id=...` — pull tasks in a specific column (e.g., "blocked", "in review")
5. `GET /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments` — read existing blocker / handoff notes
6. `GET /v1/workspaces/{workspace_id}/projects/{project_id}/activities?limit=20` — recent events for the project (`task.status_changed`, `task.assignee_added`, etc., with `metadata.old_status` / `new_status`)
7. `GET /v1/workspaces/{workspace_id}/my-tasks` — when the diagnostic is "what should *I* do next" across the workspace
8. `GET /v1/workspaces/{workspace_id}/members` — only when reassignment is the next move

For any write that follows the diagnosis, see the owning sub-skill's `api.md`.

## Diagnostic rules

- **Read current task and project state before answering.** Never give blocker advice from memory or assumption. The activity log alone is not enough — read the underlying records.
- **Use the project detail GET first.** It returns up to 200 tasks + milestones + task statuses inline, which is enough for most blocker analyses without additional round trips.
- **Group tasks by `milestone_id`** to see whether a milestone's task path is broken (no tasks linked, all tasks blocked, all tasks done but milestone still open, etc.).
- **`is_done` is per-status, not derivable from name.** Use the status's `is_done` flag, not the name, to identify "complete" vs. "in flight."
- **Look at `due_date` against the current date** to identify overdue tasks. The agent has the current date in its context.
- **For "blocked" detection, treat these as signals:**
  - status name containing `blocked`, `waiting`, `on hold`, `paused`
  - missing assignee (`assignees: []`) when a status implies someone should be working
  - `due_date` in the past with status not `is_done`
  - milestone past `end_date` with linked tasks not `is_done`
  - long gap since the task's `updated_at` for an "in progress" status
- **Activity context is cursor-paginated.** Use `before=<id>` from `next_before`, not arithmetic offsets. See `status-review/references/api.md` for the activity envelope shape.

## Possible next-move handoffs

After diagnosis, the skill that owns the next concrete write:

| Diagnosis | Next move | Owning skill |
|---|---|---|
| Task is blocked but no comment explains why | Add a blocker comment | `comments` |
| Task needs an assignee | Add assignee via sub-resource | `task` |
| Task needs a status change (e.g., move to "Blocked", "In Review") | PATCH task `status_id` (or use reorder for cross-column moves) | `task` |
| Task should be linked to a milestone | PATCH task `milestone_id` | `task` |
| Task is too broad — needs decomposition | Create child tasks | `task` |
| Blocker is project-level (e.g., missing lead, stale dates, no next move) | PATCH project / post project update | `project` / `project-updates` |
| Blocker is a missing phase | Create a milestone first | `milestone` |
| Blocker is missing categorization for filtering / reporting | Apply or create a label | `labels` |
| Stakeholders need to know about the blocker | Post a project update | `project-updates` |
| Reassignment to another team member | Add new assignee, optionally remove old one; check workspace membership | `workspace` + `task` |
| Long-form unblock plan | Save under task or project home | `persistent-files` |

## Verification rules (when this skill triggers a write through a sub-skill)

This skill rarely writes directly, but when it triggers a write through a sub-skill:

- **Read field schemas before the first write to a resource type** in this conversation (read the sub-skill's `references/api.md`). The Workpods API silently drops unknown fields.
- **GET the record back** after the write and compare each field you intended to set against what came back. Don't trust a 200 response.
- **Surface what's still blocked**, not just what was unblocked. If you cleared one blocker but two more are visible, name them.
- **End with one specific next action**, not a generic recommendation. Name the actual task, person, status, or comment.

## Cross-cutting gotchas

- **Don't answer with abstract productivity advice** when workspace state reveals a concrete next move. The whole point of this skill is grounded action.
- **Don't hide a blocker behind a status summary.** "5 tasks in progress" is not a diagnosis — name the one that's actually stuck.
- **Don't rely on activity to prove a thing happened or didn't.** Activity is best-effort and append-only; missing rows are possible. Re-read the underlying record when in doubt.
- **The Workpods API silently drops unknown fields.** When this skill triggers a sub-skill's write, the same verify-by-read-back rule applies — don't claim "unblocked" without confirming the change persisted.
