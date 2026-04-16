# Milestone API Reference

## Core endpoints

- `GET /v1/workspaces/{workspace_id}/milestone-statuses`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/milestones`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/milestones`
- `PATCH /v1/workspaces/{workspace_id}/projects/{project_id}/milestones/{milestone_id}`

## Notes

- Milestone routes require both `workspace_id` and `project_id`.
- Read the full project when you need both milestones and tasks in one view.
- Use milestone statuses, not task or project statuses.
