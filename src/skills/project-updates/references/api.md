# Project Updates API Reference

## Core endpoints

- `GET /v1/workspaces/{workspace_id}/projects/{project_id}/updates`
- `POST /v1/workspaces/{workspace_id}/projects/{project_id}/updates`
- `PATCH /v1/workspaces/{workspace_id}/projects/{project_id}/updates/{update_id}`
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/updates/{update_id}`

## Notes

- Updates are project-scoped.
- Use project detail, recent task state, or activity as the factual basis before drafting.
- Treat edits and deletes as sensitive because authorship rules may apply.
