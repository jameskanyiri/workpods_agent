# Labels API Reference

Source of truth: `workpods_backend/app/features/admin/label/api/schemas.py` (no dedicated backend doc — derive from the schemas and the route definitions in `label_api.py` / `label_category_api.py`).

Labels are unified across project, task, and milestone via the `entity_scopes` array — there is no separate `/task-labels` endpoint despite what the older `task-api.md` narrative suggests. Use the unified `/labels` endpoint with `entity_type=` filtering.

## Endpoints

Labels (workspace-scoped):

- `GET    /v1/workspaces/{workspace_id}/labels?entity_type={project|task|milestone}` — list (filter by scope)
- `POST   /v1/workspaces/{workspace_id}/labels`                                       — create
- `PATCH  /v1/workspaces/{workspace_id}/labels/{label_id}`                            — update
- `DELETE /v1/workspaces/{workspace_id}/labels/{label_id}`                            — delete (cascades removal from all linked entities)

Label categories (swimlane-style grouping):

- `GET    /v1/workspaces/{workspace_id}/label-categories`                             — list
- `POST   /v1/workspaces/{workspace_id}/label-categories`                             — create
- `PATCH  /v1/workspaces/{workspace_id}/label-categories/reorder`                     — reorder
- `PATCH  /v1/workspaces/{workspace_id}/label-categories/{category_id}`               — update
- `DELETE /v1/workspaces/{workspace_id}/label-categories/{category_id}?move_to={uuid}` — delete (must reassign if labels exist)

Application to entities (sub-resources — these live on the entity routes, not on `/labels`):

- `POST   /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels`              — link a label to a task
- `DELETE /v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/labels/{label_id}`   — unlink a label from a task
- For project labels, pass `label_ids: [UUID]` in the project create/update body (see `project/references/api.md`).
- For milestone labels, the milestone create/update body does not currently accept `label_ids` — milestone labelling is not yet wired through. Confirm the latest schema before promising milestone labels.

## Request body fields

### POST `/.../labels` — Create Label

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | string | yes | — | 1–50 chars |
| `color` | string | no | `#6B7280` | Hex (≤ 7 chars) |
| `category_id` | UUID | no | null | Must belong to the same workspace |
| `entity_scopes` | string[] | no | `[]` | Subset of `["project", "task", "milestone"]` — empty `[]` means "no enforced scope" but does not auto-broadcast; set the scopes the label is valid for |

### PATCH `/.../labels/{label_id}` — Update Label

All fields optional:

| Field | Type | Notes |
|---|---|---|
| `name` | string | 1–50 chars |
| `color` | string | Hex (≤ 7 chars) |
| `category_id` | UUID | — |
| `entity_scopes` | string[] | Replaces the existing scope array — pass the full intended set, not a delta |

### POST `/.../label-categories` — Create Category

| Field | Type | Required | Default |
|---|---|---|---|
| `name` | string | yes | — (1–50 chars) |
| `color` | string | no | `#6B7280` |

### PATCH `/.../label-categories/reorder` — Reorder Categories

| Field | Type | Notes |
|---|---|---|
| `category_ids` | UUID[] | Order in which categories should appear (assigns positions 1000, 2000, 3000…) |

### POST `/.../tasks/{task_id}/labels` — Link Label to Task

| Field | Type | Required | Notes |
|---|---|---|---|
| `label_id` | UUID | yes | Label must belong to the same workspace and have `task` in `entity_scopes` if scopes are enforced for this label |

## Response shape

`LabelOut`:

```
id              UUID
workspace_id    UUID
name            string
color           string
category_id     UUID?
entity_scopes   string[]      ← e.g. ["task"], ["project", "task"]
usage_count     int           ← computed across all linked entities
created_at      datetime?
```

`LabelCategoryOut`:

```
id              UUID
workspace_id    UUID
name            string
color           string
position        int
created_at      datetime?
updated_at      datetime?
```

## Status / reference-data lookups

Before creating a label or applying one:

1. `GET /labels?entity_type=<scope>` to see existing labels for the relevant entity scope. **Always read first** — duplicates are the most common labelling failure.
2. `GET /label-categories` if the user is grouping labels into categories or needs to name a new one consistently.

## Gotchas

- **The API silently drops unknown fields** (Pydantic `extra="ignore"` default). After every label create or update, GET the label back and confirm `name`, `color`, `category_id`, and `entity_scopes` came through correctly.
- **Read existing labels first.** Near-duplicates (`Bug` vs `Bugs`, `Site Visit` vs `Site-visit`) erode the value of labels for filtering. If a similar label already exists, link to it instead of creating a new one.
- **`entity_scopes` is a positive list, not a deny-list.** A label with `entity_scopes=["task"]` is intended for tasks; the API may not strictly enforce this on link, but downstream filters and UI assume it. Keep scopes honest.
- **Update replaces `entity_scopes` wholesale.** Pass the complete intended array on PATCH, not a delta. Sending `["milestone"]` on a label currently scoped `["task"]` removes the task scope.
- **Task-label application uses task sub-resource routes** (`POST /tasks/{task_id}/labels` with `{ "label_id": ... }`), not a body field on the task itself.
- **Project labels are passed inline.** Project create/update accepts `label_ids: [UUID]` in the body. Don't try to use a sub-resource for projects.
- **Label deletion cascades the link, not the entity.** Deleting a label removes it from every task/project that linked to it; the entities themselves survive.
- **Category deletion requires reassignment.** If labels still belong to the category, pass `?move_to={category_id}` to move them; otherwise the delete is blocked.
- **`usage_count` is computed.** Don't try to write to it. Use it as a signal for label health (high count = useful; zero = candidate for cleanup).
- **Labels are not a substitute for status or priority.** Use them for cross-cutting filters (site, team, client stream, risk type) — not to compensate for unclear titles or to recreate state semantics.

## Cascade behavior

| Action | Effect |
|---|---|
| Delete workspace | Cascades to all labels and label categories |
| Delete label | Removes link from every task / project (entities survive) |
| Delete category | Restricted if labels are still in it — pass `?move_to={uuid}` to reassign first |
| Delete task | Removes that task's label links (labels survive) |
| Delete project | Removes that project's label links (labels survive) |
