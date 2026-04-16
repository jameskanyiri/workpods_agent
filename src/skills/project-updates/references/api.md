# Project Updates API Reference

Source of truth: `workpods_backend/app/features/admin/project/api/project_update_api.py` and `workpods_backend/app/features/admin/project/api/schemas.py` (`CreateProjectUpdateRequest`, `UpdateProjectUpdateRequest`, `ProjectUpdateOut`).

Project updates are short, append-style stakeholder checkpoints attached to a project. They are **not**: long-form documents (use `persistent-files`), task-execution notes (use `comments`), or open-ended discussion (use `threads`).

## Endpoints

- `GET    /v1/workspaces/{workspace_id}/projects/{project_id}/updates`                  — list (paginated, newest first)
- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/updates`                  — create
- `PATCH  /v1/workspaces/{workspace_id}/projects/{project_id}/updates/{update_id}`      — update
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/updates/{update_id}`      — delete

The latest update for a project is also embedded in the project detail response (`GET /projects/{project_id}` → `latest_update`), and `updates_count` is computed there too.

## Request body fields

### POST `/.../updates` — Create Project Update

| Field | Type | Required | Notes |
|---|---|---|---|
| `content` | string | yes | Min length 1. Treat as Markdown. Keep it concise — this is a checkpoint, not a brief. |

### PATCH `/.../updates/{update_id}` — Edit Project Update

| Field | Type | Required | Notes |
|---|---|---|---|
| `content` | string | yes | Min length 1. Authorship rules apply server-side. |

### Query params on list

| Param | Type | Default | Notes |
|---|---|---|---|
| `skip` | int | `0` | ≥ 0 |
| `limit` | int | `50` | 1–100 |

## Response shape

`ProjectUpdateOut`:

```
id           UUID
project_id   UUID
user_id      UUID         ← author
content      string
created_at   datetime?
updated_at   datetime?    ← non-null after edit
```

List response: `data: list[ProjectUpdateOut]` + `total: int`.

## Status / reference-data lookups

Before drafting an update:

1. `GET /projects/{project_id}` — read current project, recent tasks, milestones, latest update. The factual basis for the new update lives here.
2. `GET /projects/{project_id}/activities?limit=20` only when the user wants a "since last update" recap. Updates are not the same as activity log rows — activity is auto-generated, updates are deliberate communication.

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). After a create or edit, GET the update back and confirm `content` matches what you sent and `updated_at` advanced as expected on edits.
- **Updates are project-scoped, not task-scoped.** If the note is really about one task's execution, it belongs in `comments`. If it's broader open-ended discussion, prefer `threads`.
- **Edit/delete may be author-only.** The backend service applies authorship rules (the same pattern as task comments). Treat 403 here as "not the author of this update", not "you don't have access to the project".
- **Don't post vague updates.** Each update should reference current project state — what changed, what's blocked, what the next move is. If the draft can't cite a real fact from the project, don't post it.
- **Don't dump long-form briefs into an update.** If the draft starts to read like a plan, review, or report, save it via `persistent-files` instead and reference its path in the update.
- **For client-facing drafts, scrub internal-only phrasing** before posting. The user owns the audience choice, but the agent should default to neutral language for updates marked client-facing.
- **Markdown is rendered.** Headings, lists, links, bold/italic all work. Don't HTML-escape the content.

## Cascade behavior

| Action | Effect |
|---|---|
| Delete project | Cascades to all project updates |
| Delete update | Hard delete, no soft-delete; the row is gone |
