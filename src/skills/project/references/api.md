# Project API Reference

Source of truth: `workpods_backend/docs/PROJECTS_API.md` (narrative — note: that doc only documents a small subset of the request body. The Pydantic schemas at `workpods_backend/app/features/admin/project/api/schemas.py` are canonical and accept many more fields.) When narrative and schema disagree, **trust the schema**.

## Endpoints

Project CRUD (workspace-scoped):

- `POST   /v1/workspaces/{workspace_id}/projects`                          — create
- `GET    /v1/workspaces/{workspace_id}/projects`                          — list (paginated; filter `is_starred`, `is_archived`)
- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}`             — get one (returns embedded `tasks`, `task_statuses`, `milestones`, latest update)
- `PATCH  /v1/workspaces/{workspace_id}/projects/{project_id}`             — update
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}`             — hard delete

Project statuses (workspace-scoped — read these BEFORE writing a project if `status_id` matters):

- `GET    /v1/workspaces/{workspace_id}/project-statuses`                  — list
- `POST   /v1/workspaces/{workspace_id}/project-statuses`                  — create
- `PATCH  /v1/workspaces/{workspace_id}/project-statuses/reorder`          — reorder
- `PATCH  /v1/workspaces/{workspace_id}/project-statuses/{status_id}`      — update
- `DELETE /v1/workspaces/{workspace_id}/project-statuses/{status_id}?move_to_status_id={uuid}` — delete (must reassign)

Project status categories (swimlanes):

- `GET    /v1/workspaces/{workspace_id}/project-status-categories`         — list
- `POST   /v1/workspaces/{workspace_id}/project-status-categories`         — create
- `PATCH  /v1/workspaces/{workspace_id}/project-status-categories/{category_id}` — update
- `DELETE /v1/workspaces/{workspace_id}/project-status-categories/{category_id}?move_to_category_id={uuid}` — delete

Members (workspace-scoped — read before assigning `lead_user_id` or `member_ids`):

- `GET    /v1/workspaces/{workspace_id}/members`                           — list workspace members

Workspace bootstrap:

- `GET    /v1/workspaces/default`                                          — resolve current workspace ID

Project ↔ thread management and project updates live in adjacent skills (`threads`, `project-updates`).

Never use flat paths like `/v1/projects`.

## Request body fields

### POST `/.../projects` — Create Project

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | string | yes | — | Display name |
| `code` | string | no | null | ≤ 50 chars (e.g. `P001`) |
| `summary` | string | no | null | Short summary |
| `description` | string | no | null | Long description |
| `status_id` | UUID | no | null | Must come from `project-statuses` for this workspace |
| `priority` | string | no | null | Free-form (no enum enforced server-side) |
| `lead_user_id` | UUID | no | null | Must be a workspace member |
| `member_ids` | UUID[] | no | `[]` | Workspace member UUIDs |
| `label_ids` | UUID[] | no | `[]` | Workspace label UUIDs (see `labels` skill) |
| `color` | string | no | null | Hex (e.g. `#FF5733`) |
| `icon` | string | no | null | Emoji or icon identifier |
| `start_date` | date (YYYY-MM-DD) | no | null | — |
| `end_date` | date (YYYY-MM-DD) | no | null | — |
| `metadata` | object | no | null | Free-form JSON |

**There is no `target_date` field.** When the user says "target date", set `end_date`. The backend silently drops unknown fields, so `target_date` will return 200 and leave `end_date` null.

### PATCH `/.../projects/{project_id}` — Update Project

All fields optional. Same shape as create plus the toggles:

| Field | Type | Notes |
|---|---|---|
| (all create fields) | — | Pass only the fields you want to change |
| `is_starred` | bool | Star/unstar |
| `is_archived` | bool | Archive/unarchive (soft hide; DELETE is hard delete) |

## Response shape

`ProjectOut` (returned by GET, POST, PATCH `data` field):

```
id                     UUID
code                   string?
name                   string
summary                string?
description            string?
workspace_id           UUID
created_by             UUID
status_id              UUID?         ← read back to verify
priority               string?       ← read back to verify
lead_user_id           UUID?         ← read back to verify
member_ids             UUID[]        ← read back to verify
labels                 LabelOut[]
is_starred             bool
is_archived            bool
color                  string?
icon                   string?
start_date             date?         ← read back to verify
end_date               date?         ← read back to verify
metadata               object?
thread_count           int
task_count             int
completed_task_count   int
updates_count          int
latest_update          ProjectUpdateOut?
tasks                  TaskOut[]      (up to 200, only on GET /{project_id})
task_statuses          TaskStatusOut[] (only on GET /{project_id})
milestones             MilestoneOut[] (up to 200, only on GET /{project_id})
created_at             datetime?
updated_at             datetime?
```

List response wraps `data: list[ProjectOut]` with a `total: int`.

## Status / reference-data lookups

Before writing a project where these fields matter:

1. `GET /workspaces/default` to resolve `workspace_id` if not already known.
2. `GET /project-statuses` to find the `status_id` for the lifecycle stage the user described (Lead, Site Assessment, Proposal Sent, Ongoing, Under War, Current MC, Expired MC, Cancelled, Lost Lead, etc.). Never invent a status_id.
3. `GET /members` if the request involves `lead_user_id` or `member_ids`. Match by name to UUID.
4. `GET /labels` (see `labels` skill) if `label_ids` are needed.

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). A 200 response does not mean your fields persisted. After every project create or update, GET the project back and confirm each field you intended to set (`name`, `status_id`, `start_date`, `end_date`, `lead_user_id`, `member_ids`, `priority`, `color`, `icon`, etc.) appears populated in the response. If a field came back null when you sent a value, the write failed silently — repair before reporting done.
- **No `target_date` field exists.** When a user says "target date", "deadline", or "due date" for a project, map to `end_date`.
- **The backend doc PROJECTS_API.md is incomplete.** It only documents `name`, `description`, `color`, `icon`, `metadata` for the create body. The actual API also accepts `code`, `summary`, `status_id`, `priority`, `lead_user_id`, `member_ids`, `label_ids`, `start_date`, `end_date`. Use those — they are real and persisted.
- **Project access is ownership-based.** Only the creator can view/edit/delete their own projects (in addition to workspace membership checks). If a write fails with 403 on a project the user can clearly see, it may be a different user's project.
- **`thread_count`, `task_count`, `completed_task_count`, `updates_count` are computed.** Never try to write to them. Treat them as read-only health signals.
- **`is_archived` is a soft hide, not a delete.** DELETE is a permanent, cascading hard delete (kills tasks, milestones, all task children). Confirm before calling DELETE.
- **`ON DELETE SET NULL` for threads.** Deleting a project sets `project_id = NULL` on its threads (threads survive). Tasks and milestones are cascaded.
- **Project statuses are workspace-scoped.** Don't reuse status IDs from another workspace — `STATUS_WORKSPACE_MISMATCH`-class errors will fire.
- **No project-level priority enum.** `priority` is a free-form string on projects (different from tasks, which enforce `urgent|high|medium|low|none`).

## Error codes

Project routes emit standard validation errors (`400`), auth errors (`401`/`403`), and `404` for missing resources. Common conditions:

| Status | Condition |
|---|---|
| 400 | Validation error, workspace mismatch, thread already assigned to another project |
| 403 | Not a workspace member, or not the project owner |
| 404 | Project, thread, status, member, or label not found |

Project-status routes follow the same `*_WORKSPACE_MISMATCH`, `LAST_STATUS`, `STATUS_HAS_*`, `INVALID_MOVE_TARGET` pattern as milestone statuses (see `milestone/references/api.md`).

## Cascade behavior

| Action | Effect |
|---|---|
| Delete workspace | Cascades to all projects, milestones, tasks, statuses, labels |
| Delete project | Hard delete — cascades to all milestones and tasks (and their comments, images, assignees, label links). Threads' `project_id` is set to NULL (threads survive). |
| Archive project | Soft hide via `is_archived=true`. No data deleted. |
