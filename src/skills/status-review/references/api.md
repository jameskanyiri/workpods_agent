# Status Review API Reference

This skill is **read-heavy**. It synthesizes a review from existing project, milestone, task, activity, and update data without (usually) writing back. Source of truth: `workpods_backend/docs/PROJECTS_API.md`, `workpods_backend/docs/MILESTONES_API.md`, `workpods_backend/docs/task-api.md`, `workpods_backend/docs/ACTIVITY_API.md`, plus the matching Pydantic schemas. For writes (status changes, posting an update), hand off to the owning skill instead of writing from this skill.

## Endpoints

The single most important endpoint — returns project + tasks + task statuses + milestones in one round trip:

- `GET /v1/workspaces/{workspace_id}/projects/{project_id}` — full project detail (embeds up to 200 tasks, all task statuses, up to 200 milestones, latest update)

Reference data needed to interpret the project view:

- `GET /v1/workspaces/{workspace_id}/project-statuses`     — project lifecycle statuses (with `is_done` semantics)
- `GET /v1/workspaces/{workspace_id}/milestone-statuses`   — milestone lifecycle statuses
- `GET /v1/workspaces/{workspace_id}/task-statuses`        — task Kanban columns
- `GET /v1/workspaces/{workspace_id}/labels?entity_type={project|task|milestone}` — labels for filtering
- `GET /v1/workspaces/{workspace_id}/members`              — to resolve actor / lead / assignee names

Cross-cutting tasks for "what should I do next":

- `GET /v1/workspaces/{workspace_id}/my-tasks`             — tasks assigned to the current user across the entire workspace (returns embedded `statuses`)

Activity and updates (for narrative/recency context):

- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/activities` — append-only activity log scoped to this project (cursor-paginated, `limit` ≤ 200, `before` cursor)
- `GET /v1/workspaces/{workspace_id}/activities`           — workspace-wide activity feed
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/updates`    — project updates (handoff to `project-updates` skill for writes)

## Request body fields

This skill does not write. If a write is needed (status change, post update, comment, durable file), hand off:
- status changes on a project / milestone / task → `project-execution` or the owning resource skill
- posting an update → `project-updates`
- saving the review as a durable doc → `persistent-files`

## Response shape

Returned by `GET /projects/{project_id}` (the workhorse for status review):

```
ProjectOut {
  id, code, name, summary, description, workspace_id, created_by,
  status_id, priority, lead_user_id, member_ids, labels,
  is_starred, is_archived, color, icon,
  start_date, end_date,
  thread_count, task_count, completed_task_count, updates_count,
  latest_update,
  tasks:          TaskOut[]      (up to 200)
  task_statuses:  TaskStatusOut[]
  milestones:     MilestoneOut[] (up to 200)
  created_at, updated_at,
}
```

Each `TaskOut` carries `status_id`, `priority`, `due_date`, `assignees`, `labels`, `milestone_id` — enough to compute progress, blockers, overdue work, and milestone groupings.

Each `MilestoneOut` carries `status_id`, `start_date`, `end_date` — pair with tasks (filter `tasks` by `milestone_id`) to compute milestone progress.

`ActivityLogOut` (returned by `/activities`):

```
{
  id, actor: { id, first_name, last_name, avatar_url, email },
  event_type, entity_type, entity_id, entity_name,
  metadata, created_at,
}
```

Tracked event types include `project.created/updated/archived/deleted`, `milestone.created/updated/deleted`, `task.created/updated/status_changed/deleted/assignee_added/removed/comment_added`. `task.status_changed` carries `metadata.old_status` and `metadata.new_status`.

Activities use **cursor pagination**, not offset: pass the `next_before` value from the previous response as `?before=...` to load older events. `next_before: null` means end of feed.

## Status / reference-data lookups

Order of reads for a typical status review:

1. Resolve workspace (`workspace` skill) and target project.
2. `GET /projects/{project_id}` once — gives you tasks, milestones, task statuses, and the latest update inline.
3. `GET /project-statuses` and `GET /milestone-statuses` to interpret the lifecycle stages by name and to identify `is_done` columns.
4. `GET /members` if assignees need to be named for the user.
5. `GET /projects/{project_id}/activities?limit=50` only when the review needs recent narrative ("what changed in the last week").
6. `GET /projects/{project_id}/updates` only when you need stakeholder-facing checkpoints for context.
7. `GET /my-tasks` only for "what should I work on next" reviews scoped to the current user.

Avoid pulling activity if a structural review answers the user's question — activity is a heavier read.

## Gotchas

- **Read first, never answer from memory.** A status review based on a stale recollection is a bug, not a feature. The whole point of this skill is reading current state before advising.
- **Use milestones AND tasks together.** Reviewing milestones in isolation hides whether tasks are actually progressing; reviewing tasks in isolation hides phase context. Group tasks by `milestone_id`.
- **`is_done` is per-status, not derivable from name.** `Done`, `Completed`, `Closed`, `Won` are all candidate "done" statuses depending on workspace. Check the status's `is_done` flag, not its name.
- **Project tasks list is capped at 200.** For large projects, paginate via `/projects/{project_id}/tasks` with `skip`/`limit`. The embedded `tasks` on the project detail response truncates silently.
- **Project milestones list is also capped at 200.** Same pattern — paginate via `/projects/{project_id}/milestones`.
- **Activity is append-only and best-effort.** Missing rows are possible (logging never blocks the main op). Don't treat absence of an activity event as proof an action didn't happen — re-read the underlying record instead.
- **Cursor pagination, not offset.** Activity endpoints take `before=<id>`, not `skip=N`. Don't try to compute pages with arithmetic; use `next_before` from the prior response.
- **`task.status_changed` includes `old_status` and `new_status` in `metadata`.** Use those to identify forward progress vs. regressions.
- **Lead with blocked, overdue, or high-risk work.** Optimistic summaries that hide blockers are an anti-pattern. The user reads a status review to find what to do next, not to feel good about the past.
- **End with one specific next move.** Counts and percentages are not a recommendation. Name the actual task, milestone, or owner that needs to act.
- **If the review should persist or be posted, hand off.** This skill does not write. `project-updates` posts; `persistent-files` saves a durable doc.

## Error codes

Read-only routes mostly return:

| HTTP | Condition |
|---|---|
| 401 | Not authenticated / invalid token |
| 403 | Not a workspace member (or, for org/super-admin activity, missing org or super-admin permission) |
| 404 | Project, milestone, task, or activity log not found |
