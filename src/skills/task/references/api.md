# Task API Reference

## Core endpoints

- `GET /v1/workspaces/{workspace_id}/task-statuses`
- `GET /v1/workspaces/{workspace_id}/members`
- `GET /v1/workspaces/{workspace_id}/labels`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/tasks`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/tasks`
- `PATCH /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/assignees`
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/assignees/{user_id}`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels`
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels/{label_id}`
- `GET /v1/workspaces/{workspace_id}/my-tasks`

## Notes

- Task routes require both `workspace_id` and `project_id`.
- Assignees and labels are sub-resource writes.
- Use the project detail or list route to check for duplicates before creation.
