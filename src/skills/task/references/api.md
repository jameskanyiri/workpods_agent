# Task API Reference

Source of truth: `workpods_backend/docs/task-api.md` (narrative) and `workpods_backend/app/features/admin/task/api/schemas.py` (canonical field list — when narrative and schema disagree, trust the schema).

## Endpoints

Task CRUD (workspace + project scoped):

- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/tasks`                  — create
- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/tasks`                  — list (filter `status_id`, `priority`, `assigned_to`, `label_id`, `search`; paginated)
- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}`        — get one
- `PATCH  /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}`        — update
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}`        — delete
- `PATCH  /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/reorder`          — drag-and-drop reorder

Cross-workspace user view:

- `GET    /v1/workspaces/{workspace_id}/my-tasks`                                     — tasks assigned to the current user (returns embedded `statuses` for rendering)

Task statuses (workspace-scoped — read these BEFORE writing a task if `status_id` matters):

- `GET    /v1/workspaces/{workspace_id}/task-statuses`                                — list
- `POST   /v1/workspaces/{workspace_id}/task-statuses`                                — create
- `PATCH  /v1/workspaces/{workspace_id}/task-statuses/reorder`                        — reorder
- `PATCH  /v1/workspaces/{workspace_id}/task-statuses/{status_id}`                    — update
- `DELETE /v1/workspaces/{workspace_id}/task-statuses/{status_id}?move_to_status_id={uuid}` — delete (must reassign)

Task assignees (sub-resource):

- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/assignees`           — add
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/assignees/{user_id}` — remove

Task labels (sub-resource — labels themselves live in the `labels` skill):

- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels`              — link a label
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels/{label_id}`   — unlink a label

Task comments (sub-resource — see `comments` skill for full surface):

- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments`            — list
- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments`            — add
- `PATCH  /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}` — update (author only)
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}` — delete (author only)

Task images (sub-resource):

- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/images`              — list
- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/images`              — upload (multipart/form-data, max 10 MB, JPEG/PNG/GIF/WEBP/SVG)
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/images/{image_id}`   — delete

Members (workspace-scoped — read before assigning):

- `GET    /v1/workspaces/{workspace_id}/members`                                      — list workspace members

Reading the parent project (`GET /v1/workspaces/{workspace_id}/projects/{project_id}`) returns up to 200 tasks embedded — use it when you need a project-wide task view in one round trip.

Never use flat paths like `/v1/tasks`.

## Request body fields

### POST `/.../tasks` — Create Task

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `title` | string | yes | — | 1–500 chars |
| `code` | string | no | null | ≤ 50 chars |
| `description` | string | no | null | Markdown supported |
| `status_id` | UUID | no | workspace default task status | Must belong to the same workspace |
| `priority` | string | no | `"none"` | One of: `urgent`, `high`, `medium`, `low`, `none` |
| `milestone_id` | UUID | no | null | Link to a project milestone |
| `due_date` | date (YYYY-MM-DD) | no | null | — |
| `thread_id` | UUID | no | null | Link to an existing thread |

Tasks have a `due_date` (the date a single unit of work is due) — this is the closest analog to a milestone's `end_date`. Don't confuse them.

### PATCH `/.../tasks/{task_id}` — Update Task

All fields optional. Same shape as create:

| Field | Type | Notes |
|---|---|---|
| `title` | string | 1–500 chars |
| `code` | string | ≤ 50 chars |
| `description` | string | — |
| `status_id` | UUID | If changed, the task is repositioned at the end of the new column |
| `priority` | string | `urgent` / `high` / `medium` / `low` / `none` |
| `milestone_id` | UUID or `null` | Pass `null` to unlink from current milestone |
| `due_date` | date or `null` | — |
| `thread_id` | UUID or `null` | — |

### PATCH `/.../tasks/reorder` — Drag & Drop

| Field | Type | Notes |
|---|---|---|
| `task_id` | UUID | required |
| `status_id` | UUID | required (target column) |
| `position` | float | required (client-computed midpoint between neighbors) |

### POST `/.../assignees` — Add Assignee

`{ "user_id": "uuid" }` — must be a workspace member.

### POST `/.../labels` — Add Label to Task

`{ "label_id": "uuid" }` — label must belong to the same workspace.

### POST `/.../comments` — Add Comment

`{ "content": "string" }` — `content` is required, min length 1.

## Response shape

`TaskOut` (returned by GET, POST, PATCH `data` field):

```
id              UUID
code            string?
title           string
project_name    string?         (populated on my-tasks responses)
description     string?
project_id      UUID
workspace_id    UUID
status_id       UUID            ← read back to verify
priority        string          ← read back to verify
position        float
thread_id       UUID?           ← read back to verify
milestone_id    UUID?           ← read back to verify
due_date        date?           ← read back to verify
created_by      UUID
assignees       UUID[]          ← managed via sub-resource, read back after add/remove
labels          LabelOut[]      ← managed via sub-resource, read back after link/unlink
created_at      datetime?
updated_at      datetime?
```

`my-tasks` response additionally returns `statuses: list[TaskStatusOut]` so the client can render the Kanban without a second call.

## Status / reference-data lookups

Before writing a task where these fields matter:

1. `GET /workspaces/default` to resolve `workspace_id` if not already known.
2. `GET /task-statuses` to find a `status_id`. Defaults seeded per workspace: **To Do** (default), **In Progress**, **Done** (`is_done=true`).
3. `GET /members` if `assignees` are needed.
4. `GET /labels?entity_type=task` (see `labels` skill — there is no separate `/task-labels` endpoint; labels are unified with `entity_scopes` filtering) if `label_ids` are needed.
5. `GET /projects/{project_id}` to get embedded milestones and pick a `milestone_id` if the task should link to a phase.

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). A 200 response does not mean your fields persisted. After every task create or update, GET the task back and confirm each field you intended to set (`title`, `status_id`, `priority`, `milestone_id`, `due_date`, etc.) appears populated in the response. If a field came back null when you sent a value, the write failed silently — repair before reporting done.
- **Tasks have `due_date`, milestones have `end_date`.** Don't cross them. A task linked to a milestone keeps its own `due_date`; the milestone's date is independent.
- **`milestone_id` is nullable and survives milestone deletion.** When a milestone is deleted, `tasks.milestone_id` is set to NULL via `ON DELETE SET NULL`. The task remains. Use this to model phase changes by re-linking tasks rather than recreating them.
- **`status_id` change repositions the task.** PATCH that changes `status_id` puts the task at the end of the new status column. Use the reorder endpoint if a specific position is needed.
- **`priority` is enum-enforced.** Unlike projects, tasks reject priorities outside `urgent|high|medium|low|none`. The default is `"none"`, not null.
- **Assignees and labels are sub-resources, not body fields.** Don't try to pass `assignees` or `labels` arrays in the create body — they are managed via dedicated POST/DELETE endpoints. After adding or removing, GET the task back to confirm the link.
- **Comments and images use separate sub-resource endpoints.** Comment edit/delete is **author-only** — a 403 here means the current user didn't write that comment.
- **Status deletion requires reassignment.** Pass `?move_to_status_id={uuid}` on DELETE if the status still has tasks, or you'll be blocked.
- **Hard delete cascades.** Deleting a task deletes its comments, images, assignee links, and label links. Soft-delete is not supported at the task level; if you need to hide a task, change its status instead.
- **`my-tasks` is workspace-wide.** It crosses projects — handy for "what should I work on next" queries, but you still need the parent project to do most updates.

## Error codes

Task routes return errors as `{"detail": "..."}` (FastAPI default) rather than the structured `error_code` envelope used by milestones. Common conditions:

| Status | Condition |
|---|---|
| 400 | Validation error (invalid input, missing required fields, bad priority value) |
| 403 | Not a workspace member, or editing/deleting another user's comment |
| 404 | Task, status, label, project, comment, image, or assignee not found |
| 409 | Conflict (duplicate name, already assigned) |

## Cascade behavior

| Action | Effect |
|---|---|
| Delete workspace | Cascades to all task statuses, labels, projects, tasks |
| Delete project | Cascades to all tasks (and their comments, images, assignees, label links) |
| Delete task | Cascades to comments, images, assignee links, label links |
| Delete milestone | Sets `milestone_id = NULL` on tasks (tasks survive) |
| Delete task status | Restricted — pass `move_to_status_id` to reassign tasks first |
| Delete label | Removes from all tasks (tasks survive) |
| Delete thread | Sets `thread_id = NULL` on linked tasks (tasks survive) |
| Delete user | Removes from assignee lists, cascades comment deletion |
