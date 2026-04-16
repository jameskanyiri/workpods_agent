# Labels API Reference

## Core endpoints

- `GET /v1/workspaces/{workspace_id}/label-categories`
- `POST /v1/workspaces/{workspace_id}/label-categories`
- `PATCH /v1/workspaces/{workspace_id}/label-categories/{category_id}`
- `GET /v1/workspaces/{workspace_id}/labels`
- `POST /v1/workspaces/{workspace_id}/labels`
- `PATCH /v1/workspaces/{workspace_id}/labels/{label_id}`
- `DELETE /v1/workspaces/{workspace_id}/labels/{label_id}`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels`
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels/{label_id}`

## Notes

- Labels support `entity_scopes` such as `task`, `project`, and `milestone`.
- Read labels first so you do not create near-duplicates.
- Task label application uses task sub-resource routes.
