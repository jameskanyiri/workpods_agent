# Workspace API Reference

Source of truth: `workpods_backend/docs/WORKSPACES_API.md` and `workpods_backend/app/features/admin/workspace/api/schemas.py`.

This skill is mostly about reading workspace context and member lists so downstream project/task/milestone work has the data it needs. Workspace creation lives under organizations and is rarely the active path.

## Endpoints

Resolution and listing:

- `GET    /v1/workspaces/default`                                          — current user's default workspace (returns one `WorkspaceWithMembershipOut`)
- `GET    /v1/workspaces`                                                  — all workspaces the current user belongs to
- `GET    /v1/workspaces/{workspace_id}`                                   — one workspace
- `PUT    /v1/workspaces/default`                                          — set the user's default workspace

Workspace lifecycle:

- `POST   /v1/organizations/{organization_id}/workspaces`                  — create (org-scoped, requires `workspace.create` org permission)
- `PATCH  /v1/workspaces/{workspace_id}`                                   — update (requires `workspace.update`)
- `DELETE /v1/workspaces/{workspace_id}`                                   — delete (requires `workspace.delete`)

Members:

- `GET    /v1/workspaces/{workspace_id}/members`                           — list workspace members (with org-derived roles + permission keys)
- `POST   /v1/workspaces/{workspace_id}/members`                           — add an existing org member by email (requires `workspace.members.manage`)
- `DELETE /v1/workspaces/{workspace_id}/members/{user_id}`                 — remove a member (requires `workspace.members.manage`)
- `POST   /v1/workspaces/{workspace_id}/leave`                             — current user leaves the workspace

## Request body fields

### POST `/v1/organizations/{organization_id}/workspaces` — Create Workspace

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | string | yes | — | — |
| `icon` | string | no | null | Emoji or short icon |
| `description` | string | no | null | — |
| `slug` | string | no | null | URL-style slug |

The authenticated user is added to the new workspace automatically.

### PATCH `/v1/workspaces/{workspace_id}` — Update Workspace

All fields optional:

| Field | Type | Notes |
|---|---|---|
| `name` | string | — |
| `icon` | string | — |
| `slug` | string | — |
| `description` | string | — |

### PUT `/v1/workspaces/default` — Set Default Workspace

| Field | Type | Required | Notes |
|---|---|---|---|
| `workspace_id` | UUID | yes | Must be a workspace the user belongs to |

### POST `/v1/workspaces/{workspace_id}/members` — Add Member

| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string | yes | If the email belongs to an existing org member, they are added to the workspace; new emails receive an organization invitation with this workspace preselected. |

## Response shape

`WorkspaceWithMembershipOut` (returned by `/workspaces` and `/workspaces/default`):

```
id              UUID
name            string
icon            string?
slug            string?
organization_id UUID
created_by      UUID?
description     string?
is_active       bool
is_default      bool          ← whether this is the current user's default
member_count    int           ← computed
created_at      datetime?
updated_at      datetime?
```

`WorkspaceOut` (returned by single-workspace endpoints) is the same minus `is_default` and `member_count`.

`MemberInfo` (returned by `/members`):

```
user_id          UUID
email            string
first_name       string?
last_name        string?
role_names       string[]            ← organization roles, surfaced for convenience
permission_keys  string[]            ← e.g. workspace.update, workspace.members.manage
is_default       bool
joined_at        datetime?
avatar_url       string?
```

## Status / reference-data lookups

- Always start here: `GET /v1/workspaces/default` resolves `workspace_id` for downstream calls.
- `GET /v1/workspaces` only when the user wants to switch or pick a different workspace.
- `GET /v1/workspaces/{workspace_id}/members` before any write that takes `lead_user_id`, `member_ids`, `assigned_to`, or `assignees` — match the user's name to the real `user_id`.

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). After every workspace write (rare), GET the workspace back and confirm each field you intended to set actually appears populated.
- **`/v1/workspaces/default` returns one workspace, not a list.** Treat it as a single object response.
- **Workspace creation is no longer at `POST /v1/workspaces`.** It lives under organizations: `POST /v1/organizations/{organization_id}/workspaces`. The flat path returns 404.
- **Workspace membership ≠ organization membership.** A user must already be in the org before they can be added to a workspace. Adding by email checks org membership first; if absent, the system sends an org invite preselecting this workspace.
- **Permission keys live on org roles, not workspace roles.** When you read `MemberInfo.permission_keys`, those describe what the user can do across the org (and thus this workspace), not workspace-local permissions.
- **`is_default` is per-user.** Each user has at most one default. Setting a new default does not delete the old one — it just flips the flag. If a user leaves their default workspace, the system promotes another one when available.
- **Don't invent workspace IDs.** Always read from `/workspaces/default` or `/workspaces` first.
- **Don't ask the user to restate workspace context** if `/workspaces/default` already gives an unambiguous answer.

## Cascade behavior

- Deleting a workspace cascades to all child resources: projects, milestones, tasks, statuses, labels, threads, files. Confirm before calling DELETE.
- `POST /workspaces/{workspace_id}/leave` removes only the current user. If the workspace was the user's default, another workspace is promoted to default if any exists.

## Authorization summary

| Action | Requirement |
|---|---|
| Read workspace | Workspace membership |
| Create workspace | Org membership + `workspace.create` |
| Update workspace | Workspace membership + `workspace.update` |
| Delete workspace | Workspace membership + `workspace.delete` |
| Add/remove members | Workspace membership + `workspace.members.manage` |
| Access child resources (projects, tasks, files, …) | Workspace membership |
