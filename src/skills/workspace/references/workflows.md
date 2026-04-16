# Workspace Workflows

## Resolve workspace before downstream work

1. Read the active workspace from context if present.
2. If it is missing or stale, call `GET /v1/workspaces/default`.
3. If the user requests a different workspace, call `GET /v1/workspaces`.
4. Confirm the workspace only when the choice changes which records will be touched.
5. Fetch members if the downstream flow needs a lead, assignee, or invite target.

## Member resolution for assignments

1. Resolve workspace.
2. Call `GET /v1/workspaces/{workspace_id}/members`.
3. Match the named person against the returned members.
4. If there is no confident match, ask one direct clarifying question.
5. Pass the resolved member context to the owning skill.
