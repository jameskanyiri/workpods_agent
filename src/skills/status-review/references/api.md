# Status Review API Reference

## Core endpoints

- `GET /v1/workspaces/{workspace_id}/projects/{project_id}`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/activities`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/updates`
- `GET /v1/workspaces/{workspace_id}/my-tasks`

## Notes

- Use the project detail route first because it returns tasks and milestones together.
- Pull activity or updates only when the review needs recency or narrative context.
