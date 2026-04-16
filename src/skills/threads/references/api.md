# Threads API Reference

## Core endpoints

- `POST /v1/workspaces/{workspace_id}/threads`
- `GET /v1/workspaces/{workspace_id}/threads`
- `GET /v1/workspaces/{workspace_id}/threads/{thread_id}`
- `PATCH /v1/workspaces/{workspace_id}/threads/{thread_id}`
- `DELETE /v1/workspaces/{workspace_id}/threads/{thread_id}`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/threads`
- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/threads`
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/threads/{thread_id}`

## Notes

- Threads are workspace-scoped objects that can optionally be attached to a project.
- Project-thread routes do not create comment history; they manage association.
