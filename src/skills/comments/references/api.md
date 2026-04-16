# Task Comments API Reference

## Core endpoints

- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments`
- `PATCH /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}`
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}`

## Notes

- Comments are task-scoped.
- Edit and delete permissions may depend on authorship.
