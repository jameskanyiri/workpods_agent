# Persistent Files API Reference

Use the backend virtual filesystem as the durable document store.

## Preferred Scope Mechanism

Prefer:
- `home_type`
- `home_id`

Supported homes:
- `user`
- `workspace`
- `project`
- `milestone`
- `task`

Legacy scope fields still work for compatibility:
- `project_id`
- `milestone_id`
- `task_id`

## Core Endpoints

### Workspace-base endpoints

- `POST /v1/workspaces/{workspace_id}/files`
- `POST /v1/workspaces/{workspace_id}/files/directories`
- `GET /v1/workspaces/{workspace_id}/files/content`
- `PATCH /v1/workspaces/{workspace_id}/files/content`
- `PUT /v1/workspaces/{workspace_id}/files/content`
- `GET /v1/workspaces/{workspace_id}/files/info`
- `GET /v1/workspaces/{workspace_id}/files/ls`
- `GET /v1/workspaces/{workspace_id}/files/search`
- `GET /v1/workspaces/{workspace_id}/files/search-content`
- `PATCH /v1/workspaces/{workspace_id}/files/move`
- `DELETE /v1/workspaces/{workspace_id}/files`

### Sugar routes

- User home:
  - `POST /v1/users/{user_id}/files`
  - `POST /v1/users/{user_id}/files/directories`
  - `GET /v1/users/{user_id}/files/content`
  - `GET /v1/users/{user_id}/files/ls`
  - `GET /v1/users/{user_id}/files/search`
  - creating user-home files or directories requires organization context in the request as documented by the backend API
- Organization home:
  - supported by the backend but not the primary target for this phase

## Common Payloads

### Create file

```json
{
  "path": "/plans/resource-plan.md",
  "content": "# Resource Plan",
  "home_type": "workspace",
  "home_id": "<workspace-id>",
  "mime_type": "text/markdown"
}
```

### Create project-scoped file through workspace endpoint

```json
{
  "path": "/briefs/project-brief.md",
  "content": "# Project Brief",
  "home_type": "project",
  "home_id": "<project-id>"
}
```

### Overwrite file

```json
{
  "path": "/briefs/project-brief.md",
  "content": "# Updated Project Brief",
  "home_type": "project",
  "home_id": "<project-id>"
}
```

### Edit by find and replace

```json
{
  "path": "/plans/action-plan.md",
  "old_string": "draft",
  "new_string": "approved",
  "home_type": "project",
  "home_id": "<project-id>",
  "replace_all": false
}
```

### Move or rename

```json
{
  "old_path": "/drafts/q2-plan.md",
  "new_path": "/plans/q2-plan.md",
  "home_type": "workspace",
  "home_id": "<workspace-id>"
}
```

## Usage Guidance

- Use `POST /files` only when the file does not already exist.
- Use `PUT /files/content` when replacing the full contents of a known durable document.
- Use `PATCH /files/content` when a precise edit is safer than a full overwrite.
- Use `GET /files/info` or `GET /files/content` after writes to verify persistence.
- Use `GET /files/search` or `GET /files/ls` before creating a durable document if duplication is possible.

## Permission Model

- Workspace/project/milestone/task homes:
  - require workspace membership and `file.view` / `file.create` / `file.update` permissions as appropriate
- User home:
  - private by default
  - creation requires organization context because user files live within an organization
- Organization home:
  - requires organization permission
