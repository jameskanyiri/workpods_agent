# Persistent Files API Reference

Source of truth: `workpods_backend/docs/FILES_API.md` and `workpods_backend/app/features/admin/file/api/schemas.py`.

The backend virtual filesystem stores text content (markdown by default) addressed by absolute path within a "home" — organization, workspace, project, milestone, task, or user. Use this API for durable documents that should survive the current run; use VFS for working drafts.

All endpoints require `Authorization: Bearer <access_token>`. Do **not** pass `user_id` as a query parameter — the acting user comes from the JWT.

## Endpoints

Workspace-base routes (the primary surface — covers org/workspace/project/milestone/task homes):

- `POST   /v1/workspaces/{workspace_id}/files`                     — create file
- `POST   /v1/workspaces/{workspace_id}/files/directories`         — create directory
- `GET    /v1/workspaces/{workspace_id}/files/content`             — read file
- `PATCH  /v1/workspaces/{workspace_id}/files/content`             — find-and-replace edit
- `PUT    /v1/workspaces/{workspace_id}/files/content`             — overwrite file (file must already exist)
- `DELETE /v1/workspaces/{workspace_id}/files`                     — delete file or directory (recursive for dirs)
- `GET    /v1/workspaces/{workspace_id}/files/info`                — metadata only (no content)
- `GET    /v1/workspaces/{workspace_id}/files/ls`                  — list directory (paginated)
- `GET    /v1/workspaces/{workspace_id}/files/search`              — search by name (case-insensitive substring)
- `GET    /v1/workspaces/{workspace_id}/files/search-content`      — search by content (case-insensitive substring)
- `PATCH  /v1/workspaces/{workspace_id}/files/move`                — move/rename (recursive for dirs)

Sugar routes (same operations, home implied by URL):

- User home:         `/v1/users/{user_id}/files/...`             (user files require `organization_id` query param on create)
- Organization home: `/v1/organizations/{organization_id}/files/...`

## Request body fields

All write/edit requests share the same scope-resolution pattern:
- **Preferred:** `home_type` + `home_id` (one of `organization|workspace|project|milestone|task|user`).
- **Legacy (still accepted):** `project_id`, `milestone_id`, `task_id`. `milestone_id` and `task_id` require `project_id`.
- If `home_type/home_id` are omitted, the server derives the home as `task` > `milestone` > `project` > `workspace`.

### POST `/files` — Create File

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `path` | string | yes | — | Absolute, e.g. `/reports/summary.md`. ≤ 1024 chars. No `..` or `//`. |
| `content` | string | no | `""` | File text |
| `home_type` | string | no | (derived) | One of `organization|workspace|project|milestone|task|user` |
| `home_id` | UUID | no | null | Required when `home_type` is set |
| `project_id` | UUID | no | null | Legacy scope |
| `milestone_id` | UUID | no | null | Legacy scope (requires `project_id`) |
| `task_id` | UUID | no | null | Legacy scope (requires `project_id`) |
| `mime_type` | string | no | `text/markdown` | — |

Parent directories are auto-created.

### POST `/files/directories` — Create Directory

| Field | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | Must end with `/`, e.g. `/reports/` |
| `home_type`, `home_id`, `project_id`, `milestone_id`, `task_id` | — | no | Same as create file |

### PATCH `/files/content` — Find-and-Replace Edit

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `path` | string | yes | — | — |
| `old_string` | string | yes | — | Must appear exactly once unless `replace_all=true` |
| `new_string` | string | yes | — | — |
| `replace_all` | bool | no | `false` | — |
| `home_type`, `home_id`, `project_id`, `milestone_id`, `task_id` | — | no | — | Same scope pattern |

Errors: `STRING_NOT_FOUND`, `AMBIGUOUS_MATCH`.

### PUT `/files/content` — Overwrite Entire File

| Field | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | File must already exist (otherwise `NOT_A_FILE` or 404) |
| `content` | string | yes | Full new content |
| `home_type`, `home_id`, `project_id`, `milestone_id`, `task_id` | — | no | Same scope pattern |

### PATCH `/files/move` — Move / Rename

| Field | Type | Required | Notes |
|---|---|---|---|
| `old_path` | string | yes | — |
| `new_path` | string | yes | Fails if an entry already exists there |
| `home_type`, `home_id`, `project_id`, `milestone_id`, `task_id` | — | no | Same scope pattern |

### Read / list / search query params

`GET /files/content` accepts `path`, scope params, plus optional `offset` (>= 0, start line) and `limit` (>= 1, line count) for line-based slicing. `GET /files/info` returns metadata with `content: null`. `GET /files/ls` accepts `skip` / `limit` (1–500, default 100). `GET /files/search` and `/files/search-content` take `q` (required, non-empty), scope params, and `skip` / `limit` (1–500, default 50). Empty `q` returns `EMPTY_QUERY`.

## Response shape

`FileOut` (returned by create, read, edit, write, move, info):

```
id              UUID
organization_id UUID
workspace_id    UUID?         ← null for organization or user homes
home_type       string?
home_id         UUID?
project_id      UUID?
milestone_id    UUID?
task_id         UUID?
type            "file" | "directory"
path            string         ← read this back to verify the path you intended persisted
name            string
content         string?        ← null on info responses; full content on read responses
mime_type       string?
size_bytes      int            ← read back to confirm overwrite/edit took effect
created_by      UUID
created_at      datetime?
updated_at      datetime?      ← non-null after first edit/overwrite
```

`DirectoryEntryOut` (returned by `ls`, `search`, `search-content`) is a lightweight subset of `FileOut`: `id`, `name`, `path`, `type`, `size_bytes`, `mime_type`, `created_by`, `created_at`, `updated_at`.

## Status / reference-data lookups

Before persisting a durable document:

1. Resolve workspace via `workspace` skill if missing.
2. `GET /files/search?q=<filename>` (or `/files/ls` on the expected directory) within the target home to check whether the document already exists. Reuse over duplicate.
3. Use `GET /files/info` for metadata-only existence checks (cheaper than `/files/content`).

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). After every file create or write, GET the file back via `/files/info` or `/files/content` and confirm `path`, `home_type`, `home_id`, `mime_type`, and `size_bytes` came through correctly.
- **`PUT /files/content` does not create files.** Only existing files. Use `POST /` to create. A `NOT_A_FILE` or 404 here often means you forgot to create first.
- **Path validation is strict.** No `..`, no `//`, max 1024 chars, allowed: alphanumeric + `/` `-` `_` `.` and spaces. Files have no trailing slash; directories require one.
- **Unique path per scope.** A file at `/foo.md` in the workspace home and another at `/foo.md` in a project home can coexist. But two writes to the same `(home_type, home_id, path)` will collide as `DUPLICATE_PATH` on create.
- **Parent directories auto-create on file create**, but `/files/directories` is the explicit way to make an empty directory.
- **Directory delete is recursive.** `DELETE /files?path=/reports/` removes everything under `/reports/`. There is no soft-delete. Confirm before calling on directories.
- **Move on a directory updates all descendants** in one operation. Useful but irreversible — confirm.
- **PATCH edit requires unique `old_string`** unless `replace_all=true`. `AMBIGUOUS_MATCH` means you need more context in `old_string` or have to opt into replace-all.
- **User home creation requires organization context.** `POST /v1/users/{user_id}/files` needs `organization_id` as a query param because user files live within an organization. Other homes derive org from the workspace.
- **`workspace_id` is nullable on the row.** Org-home and user-home entries don't have a workspace. Don't assume every file you read has a `workspace_id`.
- **Authentication is JWT, not query param.** `Authorization: Bearer <access_token>`. Don't pass `user_id` in the URL or query — it comes from the token.
- **`home_type/home_id` is preferred over legacy `project_id`/`milestone_id`/`task_id`.** Use the new pair on every new write. Legacy fields are still accepted for compatibility but are being phased out.
- **`size_bytes` and `content_hash` are computed.** Don't try to write them; rely on them after a write to confirm the content you intended is what landed.

## Error codes

| `error_code` | Meaning |
|---|---|
| `INVALID_PATH` | Bad characters, `..`, `//`, length, or trailing-slash mismatch |
| `DUPLICATE_PATH` | A file or directory already exists at that scope+path |
| `PATH_REQUIRED` | No `path` provided |
| `WORKSPACE_ID_REQUIRED` | No workspace id where one was needed |
| `NOT_A_FILE` | Tried to read/edit/write a directory |
| `STRING_NOT_FOUND` | `old_string` not present in file content |
| `AMBIGUOUS_MATCH` | `old_string` matches multiple times without `replace_all` |
| `EMPTY_QUERY` | Search `q` is empty or whitespace |

| HTTP | Condition |
|---|---|
| 401 | Missing / invalid / expired / revoked JWT, inactive account |
| 403 | Insufficient workspace or org file permission (`file.view` / `file.create` / `file.update`) |
| 404 | File or directory not found |

## Cascade behavior

| FK | On delete |
|---|---|
| `organization_id` | RESTRICT (org delete blocked while files exist) |
| `workspace_id` | Cascades file rows when workspace deleted |
| `project_id` | SET NULL — file row survives, project link cleared |
| `milestone_id` | CASCADE — file row deleted with the milestone |
| `task_id` | CASCADE — file row deleted with the task |

So: files saved under a `task` or `milestone` home **are deleted** when that task/milestone is deleted; files saved under a `project` home **survive** project deletion (with `project_id` set NULL); files under `workspace` home die with the workspace.

## Permission model

| Home | Required |
|---|---|
| Workspace / project / milestone / task | Workspace membership + org permissions `file.view` / `file.create` / `file.update` |
| Organization | Org membership + org permissions |
| User | Private by default (only the same user); plus org permissions within the file's `organization_id` |

## Agent tool ↔ API mapping

When using agent tools that wrap the file API:

| Agent tool | API |
|---|---|
| `write` | `POST /files` (create) or `POST /files/directories` |
| `read` | `GET /files/content` |
| `update` | `PATCH /files/content` (edit), `PUT /files/content` (overwrite), `PATCH /files/move` (move) |
| `delete` | `DELETE /files` |
| `ls` | `GET /files/ls` |
| `search` | `GET /files/search` |
