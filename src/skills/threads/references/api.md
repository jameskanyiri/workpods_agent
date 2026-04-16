# Threads API Reference

Source of truth: `workpods_backend/app/features/admin/thread/api/api.py` and `workpods_backend/app/features/admin/thread/api/schemas.py`. Project-thread association lives in `workpods_backend/docs/PROJECTS_API.md` (Project-Thread Management section).

Threads are workspace-scoped chat conversations (originally agent threads). They can optionally be attached to one project at a time. Use them for broader discussion that spans multiple tasks or continues over time. They are **not**: project-level checkpoints (use `project-updates`), task-execution notes (use `comments`), or durable documents (use `persistent-files`).

## Endpoints

Thread CRUD (workspace-scoped):

- `POST   /v1/workspaces/{workspace_id}/threads`                                 — create
- `GET    /v1/workspaces/{workspace_id}/threads`                                 — list (filter `is_starred`, `is_archived`, `is_pinned`, `status`, `agent_name`; paginated)
- `GET    /v1/workspaces/{workspace_id}/threads/{thread_id}`                     — get one
- `PATCH  /v1/workspaces/{workspace_id}/threads/{thread_id}`                     — update
- `DELETE /v1/workspaces/{workspace_id}/threads/{thread_id}`                     — delete

Bulk operations:

- `POST   /v1/workspaces/{workspace_id}/threads/archive-all`                     — archive every thread (returns `affected_count`)
- `DELETE /v1/workspaces/{workspace_id}/threads/archived`                        — delete all archived threads
- `DELETE /v1/workspaces/{workspace_id}/threads/all`                             — delete every thread (destructive — confirm)

Project-thread association:

- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/threads`           — attach an existing thread to a project
- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/threads`           — list threads attached to a project (paginated)
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/threads/{thread_id}` — detach (sets `project_id = NULL`, thread survives)

Tasks may also link to threads via `tasks.thread_id` (see `task/references/api.md`); thread lifecycle is independent of task lifecycle.

## Request body fields

### POST `/.../threads` — Create Thread

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Display name |
| `agent_name` | string | yes | Identifier of the agent backing this thread |
| `langgraph_thread_id` | string | no | Optional LangGraph runtime ID |
| `metadata` | object | no | Flexible config (model, temperature, etc.) |

### PATCH `/.../threads/{thread_id}` — Update Thread

All fields optional:

| Field | Type | Notes |
|---|---|---|
| `name` | string | — |
| `is_starred` | bool | Star/unstar |
| `is_archived` | bool | Archive (soft hide; DELETE is hard delete) |
| `is_pinned` | bool | Pin/unpin |
| `status` | string | `active`, `completed`, `error` |
| `langgraph_thread_id` | string | — |
| `metadata` | object | — |

### POST `/projects/{project_id}/threads` — Attach Thread to Project

| Field | Type | Required | Notes |
|---|---|---|---|
| `thread_id` | UUID | yes | Validates that thread + project share the same workspace and same user, and that the thread isn't already on another project |

### Query params on list

`/threads` supports: `is_starred`, `is_archived`, `is_pinned`, `status`, `agent_name`, `skip` (≥0), `limit` (1–500, default 50).
`/projects/{project_id}/threads` supports: `skip`, `limit` (default 50, max 100).

## Response shape

`ThreadOut`:

```
id                     UUID
name                   string
workspace_id           UUID
created_by             UUID
agent_name             string
is_starred             bool         ← read back to verify
is_archived            bool         ← read back to verify
is_pinned              bool         ← read back to verify
status                 string       ← read back to verify
project_id             UUID?        ← read back to verify after attach/detach
langgraph_thread_id    string?
metadata               object?
last_activity_at       datetime?
created_at             datetime?
updated_at             datetime?
```

List response: `data: list[ThreadOut]` + `total: int`.
Bulk operations return `BulkOperationResponse{ status, affected_count, message }`.

## Status / reference-data lookups

Before threading work into a project:

1. `GET /threads` to find the thread by name or recent activity.
2. `GET /projects/{project_id}/threads` to see what's already attached (avoid duplicate attachment — a thread can only belong to one project).
3. `GET /projects/{project_id}` to confirm the user can write to that project.

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). After a create or edit, GET the thread back and confirm `name`, `status`, `is_*` flags, `metadata` came through.
- **One project per thread.** A thread's `project_id` FK lives on the threads table (one-to-many: project → many threads). Attaching a thread to a second project will fail with `THREAD_ALREADY_ASSIGNED`. Detach first if reassignment is intended.
- **Detach ≠ delete.** `DELETE /projects/{project_id}/threads/{thread_id}` clears the link only; the thread survives. To remove the thread entirely, use `DELETE /workspaces/{workspace_id}/threads/{thread_id}`.
- **Project deletion preserves threads.** Threads have `ON DELETE SET NULL` from project, so deleting a project just nulls the link.
- **Workspace deletion cascades threads.** Don't expect threads to survive workspace deletion.
- **Bulk operations are destructive.** `/threads/all` deletes every thread in the workspace. `/threads/archived` deletes every archived thread. Always confirm before calling — the affected count comes back, but by then it's done.
- **Ownership-based access.** Threads are tied to their creator (`created_by`). The attach endpoint validates that the thread and project belong to the same user. Treat 403 here as an ownership mismatch.
- **`status` is a free string** at the schema level (`active`, `completed`, `error` are conventions, not enforced). Use the conventional values to avoid drifting from UI expectations.
- **`last_activity_at` is computed/maintained server-side.** Don't try to write it.
- **Threads are not the right place for stakeholder updates.** Use `project-updates` for checkpoint communication; use `threads` for ongoing back-and-forth that spans multiple tasks or runs over time.

## Error codes

| `error_code` | Meaning |
|---|---|
| `THREAD_ALREADY_ASSIGNED` | The thread is already attached to a different project |
| `WORKSPACE_MISMATCH` | Thread and project belong to different workspaces |

| HTTP | Condition |
|---|---|
| 400 | Validation error, workspace mismatch, thread already assigned |
| 401 | Not authenticated |
| 403 | Not a workspace member, or not the thread/project owner |
| 404 | Thread, project, or attachment row not found |

## Cascade behavior

| Action | Effect |
|---|---|
| Delete workspace | Cascades to all threads |
| Delete project | Threads survive — `project_id` is set to NULL on linked threads |
| Delete thread | Sets `thread_id = NULL` on linked tasks (tasks survive) |
| Bulk delete archived | Hard-deletes every archived thread in the workspace |
