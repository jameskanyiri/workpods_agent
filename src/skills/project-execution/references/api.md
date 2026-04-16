# Project Execution API Reference

This skill is **orchestration-heavy**. It composes the resource skills rather than owning a unique API surface. Read this file to learn the *order* of calls and which sub-skill owns the truth — then read the matching sub-skill's `references/api.md` for actual field schemas before writing.

## Owning sub-skills (read these for field schemas)

For exact request bodies, response shapes, validation rules, and gotchas, defer to:

- `project/references/api.md`            — project CRUD (`POST /projects`, `PATCH /projects/{id}`)
- `milestone/references/api.md`          — milestone CRUD inside a project
- `task/references/api.md`               — task CRUD, assignees, labels, comments, images, reorder
- `project-updates/references/api.md`    — short stakeholder checkpoints
- `comments/references/api.md`           — task-level execution notes
- `threads/references/api.md`            — workspace-scoped discussions, optionally project-attached
- `labels/references/api.md`             — label CRUD and entity-scope rules
- `workspace/references/api.md`          — workspace resolution, member lookup
- `persistent-files/references/api.md`   — durable documents under `home_type/home_id`
- `status-review/references/api.md`      — read-only synthesis from project + milestones + tasks + activity

This skill must not duplicate field tables — that path leads to drift. Always read the owning sub-skill before the first write to a resource type.

## Endpoints used by the orchestration

The endpoints touched in a typical "move this project forward" flow, in roughly the order they fire:

1. `GET    /v1/workspaces/default`                                       — resolve `workspace_id`
2. `GET    /v1/workspaces/{workspace_id}/members`                        — for lead/assignees
3. `GET    /v1/workspaces/{workspace_id}/project-statuses`               — for project `status_id`
4. `GET    /v1/workspaces/{workspace_id}/milestone-statuses`             — for milestone `status_id`
5. `GET    /v1/workspaces/{workspace_id}/task-statuses`                  — for task `status_id`
6. `GET    /v1/workspaces/{workspace_id}/labels?entity_type=...`         — for label IDs
7. `GET    /v1/workspaces/{workspace_id}/projects/{project_id}`          — full read of current state (returns embedded tasks, milestones, latest update)
8. `POST/PATCH` against project, milestone, task, project-update endpoints in **dependency order** (project before milestone before task before update)
9. `GET    /v1/workspaces/{workspace_id}/projects/{project_id}` again to verify writes (every field the user mentioned must appear populated in the response)

For each write, see the owning sub-skill's `api.md` for the exact request body — never guess field names.

## Orchestration rules

- **Resolve workspace first.** Every downstream write requires `workspace_id`. Use `workspace/references/api.md`.
- **Read before write — both reference data and current state.** Reference data (statuses, members, labels) tells you what `*_id` values to use; current project state tells you what already exists so you don't recreate it.
- **Read field schemas before the first write to each resource type** in this conversation. The sub-skill's `references/api.md` documents the exact field names. The Workpods API silently drops unknown fields, so a write using guessed field names returns 200 and quietly persists nothing.
- **Write in dependency order.** Project → milestone → task → update. Don't try to create a milestone before the project exists; don't link a task to a milestone before the milestone is created.
- **Verify every write by field-level read-back.** GET the record after each write and compare each field you intended to set against what the response returned. If `start_date`, `end_date`, `lead_user_id`, `status_id`, `milestone_id`, etc. came back null when you sent values, the write failed silently — repair before reporting done.
- **Surface loose ends, don't bury them.** If the user mentioned a field (date, assignee, status) that you didn't set, name it explicitly: "you didn't give an end date for the project — want one or leave it null?" Never silently call an unset field "optional."
- **Hand off when ownership shifts.** Once the next concrete write is clear, defer to the owning sub-skill's `SKILL.md` and `references/api.md`. Don't re-implement project/milestone/task knowledge here.
- **Smallest set of writes that actually moves the work forward.** If a single milestone create unblocks the user, don't bundle it with five speculative tasks.

## Cross-cutting gotchas (apply to every sub-skill in the orchestration)

- **The Workpods API silently drops unknown fields** (Pydantic `extra="ignore"` default across all request schemas). A 200 response is not verification — always GET the record back and confirm each user-specified field appears populated.
- **There is no `target_date` field on projects or milestones.** Use `start_date` / `end_date` (both ISO `YYYY-MM-DD`). When the user says "target date", set `end_date`. Tasks have `due_date` (separate concept).
- **All `*_id` fields must come from real GET responses.** Don't invent status IDs, member IDs, label IDs, or workspace IDs.
- **Status IDs are workspace-scoped per resource type.** Three separate status systems (project, milestone, task), each scoped to a workspace. Don't reuse IDs across types or across workspaces.
- **Cascade behavior matters when sequencing.** Deleting a project cascades to milestones and tasks; deleting a milestone sets `tasks.milestone_id = NULL`; deleting a thread sets `tasks.thread_id = NULL`. See each sub-skill's `api.md` for the table.

## Verification protocol (after the multi-step flow)

When the orchestration completes, before saying "done":

1. GET the project (returns embedded tasks + milestones + latest update).
2. For each record created or updated in this run, confirm:
   - the user-specified fields appear populated in the GET response
   - linkage is correct (`milestone_id` on tasks, `lead_user_id` and `member_ids` on project, `status_id` on each)
3. Enumerate the fields the user mentioned during the conversation. For each, report **set-and-verified**, **set-but-not-verified**, or **unset**.
4. If anything came back wrong or null, repair it before claiming completion. A "verify" todo step is performative if it doesn't actually compare returned fields to intended fields.
