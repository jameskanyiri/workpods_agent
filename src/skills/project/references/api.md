# Project API Reference

## Core endpoints

- `GET /v1/workspaces/default`
- `GET /v1/workspaces/{workspace_id}/project-statuses`
- `GET /v1/workspaces/{workspace_id}/members`
- `POST /v1/workspaces/{workspace_id}/projects`
- `GET /v1/workspaces/{workspace_id}/projects`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}`
- `PATCH /v1/workspaces/{workspace_id}/projects/{project_id}`

## Notes

- Use `GET /projects/{project_id}` to verify persisted project state and to fetch embedded tasks, task statuses, and milestones.
- Status ids must come from `project-statuses`.
- Treat members as reference data to validate lead or member decisions.

## Payload gotchas

- Dates should be exact `YYYY-MM-DD`.
- Never use flat `/v1/projects` paths.
- Re-read the project after creation or update when the user cares about dates, lead assignment, or other critical metadata.
