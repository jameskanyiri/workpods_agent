# Workspace API Reference

Use these endpoints when the workflow needs workspace context before project, milestone, or task work.

## Core endpoints

- `GET /v1/workspaces/default`
  Use first when `workspace_id` is missing.

- `GET /v1/workspaces`
  Use only when the user wants to switch workspaces or the default is not the right one.

- `PUT /v1/workspaces/default`
  Use to change the default workspace. Confirm first.

- `GET /v1/workspaces/{workspace_id}/members`
  Use before assigning leads, owners, or assignees.

- `POST /v1/workspaces/{workspace_id}/members`
  Use for invites after the user supplies the target identity.

## Response notes

- `GET /v1/workspaces/default` returns a single workspace object.
- Member lookup should be treated as reference data for later writes.
- Workspace membership is a prerequisite for most downstream project and task actions.

## Payload gotchas

- Do not invent workspace ids.
- Do not ask for the workspace if the default workspace is already sufficient and unambiguous.
