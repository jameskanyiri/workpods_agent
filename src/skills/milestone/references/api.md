# Milestone API Reference

Source of truth: `workpods_backend/docs/MILESTONES_API.md` (narrative) and `workpods_backend/app/features/admin/milestone/api/schemas.py` (canonical field list — when narrative and schema disagree, trust the schema).

## Endpoints

Milestone CRUD (workspace + project scoped):

- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/milestones`            — create
- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/milestones`            — list (paginated, filterable by `status_id`)
- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}` — get one
- `PATCH  /v1/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}` — update
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}` — delete

Milestone statuses (workspace-scoped — read these BEFORE writing a milestone if `status_id` matters):

- `GET   /v1/workspaces/{workspace_id}/milestone-statuses`                              — list statuses
- `POST  /v1/workspaces/{workspace_id}/milestone-statuses`                              — create status
- `PATCH /v1/workspaces/{workspace_id}/milestone-statuses/{status_id}`                  — update status
- `PATCH /v1/workspaces/{workspace_id}/milestone-statuses/reorder`                      — reorder
- `DELETE /v1/workspaces/{workspace_id}/milestone-statuses/{status_id}?move_to_status_id={uuid}` — delete (must reassign)

Status categories (swimlane headers):

- `GET   /v1/workspaces/{workspace_id}/milestone-status-categories`                     — list
- `POST  /v1/workspaces/{workspace_id}/milestone-status-categories`                     — create
- `PATCH /v1/workspaces/{workspace_id}/milestone-status-categories/{category_id}`       — update
- `PATCH /v1/workspaces/{workspace_id}/milestone-status-categories/reorder`             — reorder
- `DELETE /v1/workspaces/{workspace_id}/milestone-status-categories/{category_id}?move_to_category_id={uuid}` — delete (must reassign)

Reading the parent project (`GET /v1/workspaces/{workspace_id}/projects/{project_id}`) returns the project with embedded `milestones` and `tasks` — use it when you need both views in one round trip.

Never use flat paths like `/v1/milestones`.

## Request body fields

### POST `/.../milestones` — Create Milestone

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | string | yes | — | 1–200 chars |
| `description` | string | no | null | — |
| `status_id` | UUID | no | workspace default milestone status | Must belong to the same workspace. If omitted and no default exists, returns `NO_DEFAULT_MILESTONE_STATUS`. |
| `start_date` | date (YYYY-MM-DD) | no | null | — |
| `end_date` | date (YYYY-MM-DD) | no | null | — |

**There is no `target_date` field.** When the user says "target date", set `end_date`. The backend silently drops unknown fields, so a write with `target_date` will return 200 and leave `end_date` null.

### PATCH `/.../milestones/{milestone_id}` — Update Milestone

All fields optional. Same shape as create:

| Field | Type | Notes |
|---|---|---|
| `name` | string | 1–200 chars |
| `description` | string | — |
| `status_id` | UUID | Must belong to the same workspace |
| `start_date` | date | — |
| `end_date` | date | — |

## Response shape

`MilestoneOut` (returned by GET, POST, PATCH `data` field):

```
id              UUID
code            string?
project_id      UUID
workspace_id    UUID
name            string
description     string?
status_id       UUID
start_date      date?         ← read this back to verify your write persisted
end_date        date?         ← read this back to verify your write persisted
created_by      UUID
created_at      datetime?
updated_at      datetime?
```

List response wraps `data: list[MilestoneOut]` with a `total: int`.

## Status / reference-data lookups

Before writing a milestone where `status_id` matters:

1. `GET /milestone-statuses` to list available statuses for this workspace. The 5 seeded defaults are **Upcoming** (default), **Active**, **Completed** (`is_done=true`), **Expired**, **Cancelled**.
2. Pick the status whose `name` matches the milestone's lifecycle stage. Pass its `id` as `status_id` on the create body.
3. If you don't pass `status_id`, the workspace default is used. If no default exists, the API returns `NO_DEFAULT_MILESTONE_STATUS`.

For status review, use `is_done` to mark completion semantics — the agent should treat `is_done=true` as "this milestone is finished," not just "active."

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). A 200 response does not mean your fields persisted. After every milestone create or update, GET the milestone back and confirm each field you intended to set (`name`, `status_id`, `start_date`, `end_date`) appears populated in the response. If a field came back null when you sent a value, the write failed silently — repair before reporting done.
- **No `target_date` field exists.** When a user says "target date", "deadline", or "due date" for a milestone, map to `end_date`. (Tasks have `due_date`; milestones do not.)
- **Status IDs are workspace-scoped.** Never invent a `status_id`. `STATUS_WORKSPACE_MISMATCH` fires if you pass a status from another workspace.
- **Tasks survive milestone deletion.** `tasks.milestone_id` is set to NULL via `ON DELETE SET NULL`. After deleting a milestone, expect tasks to remain unlinked — check task `milestone_id` if linkage matters.
- **Status deletion requires reassignment.** You cannot delete a milestone status that still has milestones assigned. Pass `?move_to_status_id={uuid}` to reassign first, or you'll get `STATUS_HAS_MILESTONES`.
- **Status category deletion requires reassignment.** Same pattern with `?move_to_category_id={uuid}`; error is `CATEGORY_HAS_STATUSES`.
- **Milestone statuses are not task or project statuses.** Three separate workspace-scoped status systems. Don't reuse IDs across them.
- **Milestone progress** is derived from linked tasks, not from milestone state alone. Filter `project.tasks` by `milestone_id` to compute progress; the milestone itself only carries lifecycle state via `status_id` and `is_done`.

## Error codes

| `error_code` | Meaning |
|---|---|
| `WORKSPACE_ID_REQUIRED` | `workspace_id` missing |
| `PROJECT_ID_REQUIRED` | `project_id` missing |
| `MILESTONE_NAME_REQUIRED` | Empty / whitespace-only name |
| `NO_DEFAULT_MILESTONE_STATUS` | No `status_id` passed and no default configured |
| `STATUS_WORKSPACE_MISMATCH` | Status belongs to a different workspace |
| `PROJECT_WORKSPACE_MISMATCH` | Project belongs to a different workspace |
| `MILESTONE_PROJECT_MISMATCH` | Milestone doesn't belong to this project |
| `DUPLICATE_STATUS_NAME` | Status name already exists in workspace |
| `DUPLICATE_CATEGORY_NAME` | Category name already exists in workspace |
| `LAST_STATUS` / `LAST_CATEGORY` | Cannot delete the only remaining one |
| `STATUS_HAS_MILESTONES` | Pass `move_to_status_id` to reassign first |
| `CATEGORY_HAS_STATUSES` | Pass `move_to_category_id` to reassign first |
| `INVALID_MOVE_TARGET` | `move_to_*_id` equals the ID being deleted |
| `CATEGORY_WORKSPACE_MISMATCH` | Move-to category belongs to a different workspace |

## Cascade behavior

| Action | Effect |
|---|---|
| Delete project | Cascades to all milestones in the project |
| Delete milestone | Sets `milestone_id = NULL` on tasks (tasks survive) |
| Delete milestone status | Restricted — must move milestones first via `move_to_status_id` |
| Delete milestone status category | Requires `move_to_category_id` if statuses exist in it |
