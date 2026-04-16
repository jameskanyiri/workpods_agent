# Task Comments API Reference

Source of truth: `workpods_backend/docs/task-api.md` (Comments section) and `workpods_backend/app/features/admin/task/api/schemas.py` (`CreateTaskCommentRequest`, `UpdateTaskCommentRequest`, `TaskCommentOut`).

Comments are short, threaded notes attached to a single task — execution status, evidence, blocker logs, handoff notes. They are **not**: project-level checkpoints (use `project-updates`), broader discussion (use `threads`), or long-form documents (use `persistent-files`).

## Endpoints

- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments`               — list (paginated, newest first)
- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments`               — add
- `PATCH  /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}`  — update (**author only**)
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}`  — delete (**author only**)

## Request body fields

### POST `/.../comments` — Add Comment

| Field | Type | Required | Notes |
|---|---|---|---|
| `content` | string | yes | Min length 1. Markdown-rendered. Keep it specific to this task. |

### PATCH `/.../comments/{comment_id}` — Update Comment

| Field | Type | Required | Notes |
|---|---|---|---|
| `content` | string | yes | Min length 1. Only the original author can update. |

### Query params on list

| Param | Type | Default |
|---|---|---|
| `skip` | int | `0` |
| `limit` | int | `50` |

## Response shape

`TaskCommentOut`:

```
id           UUID
task_id      UUID
user_id      UUID         ← author (used to enforce edit/delete permissions)
content      string
created_at   datetime?
updated_at   datetime?    ← non-null after edit
```

List response: `data: list[TaskCommentOut]` + `total: int`.

## Status / reference-data lookups

Before adding or referencing a comment:

1. `GET /projects/{project_id}/tasks/{task_id}` — confirm the task exists and read its current state so the comment can cite real facts.
2. `GET /tasks/{task_id}/comments` — read existing comments before claiming "no comments yet" or before editing one (avoid duplicating an existing note).

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). After a create or edit, GET the comment back (or list comments) and confirm `content` matches what you sent.
- **Edit and delete are author-only.** The current user must be the comment's author. A 403 here means "you didn't write this comment", not "you can't access this task".
- **Comments are task-scoped.** Don't use them to record project-level status that belongs on a project update. Don't paste long planning artifacts into a comment — those belong in `persistent-files`.
- **Read existing comments first** before adding a new one. Repeating an already-logged blocker is noise.
- **Comment content is Markdown.** Lists, links, code spans, and emphasis render. Don't HTML-escape.
- **No threading or replies.** Comments are flat. To respond to a specific comment, quote or reference it textually.
- **Hard delete.** No soft-delete — once deleted, the comment is gone. Confirm before deleting if intent is unclear.
- **Comment count is not a project health metric.** A task with many comments may just be one with a long discussion; it doesn't necessarily mean the task is healthy or unhealthy.

## Cascade behavior

| Action | Effect |
|---|---|
| Delete task | Cascades to all comments on that task |
| Delete user | Cascades to comments authored by that user |
| Delete project | Cascades to tasks → cascades to comments |
| Delete workspace | Cascades to projects → tasks → comments |
