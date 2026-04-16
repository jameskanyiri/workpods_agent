---
name: persistent-files
description: Triggered when the user wants a document to persist beyond the current agent run, be saved for later use, be shared, be browsed again, or be attached logically to a user, workspace, project, milestone, or task. Use this skill to save durable files into the backend virtual filesystem instead of leaving them only in VFS scratchpad files.
---

# Persistent Files Skill

## Purpose

Own durable document persistence in the backend virtual filesystem. This skill teaches when a document should remain a VFS draft and when it should be written into the backend files API as a persistent user, workspace, project, milestone, or task file.

Use this skill only for durable document artifacts. It does not replace direct project, task, milestone, update, comment, or thread writes.

Common incoming handoffs:
- `workspace`, `project`, `milestone`, or `task` when a document should persist
- `commercial-lifecycle` or `status-review` when a reusable review or plan should be saved

Common outgoing handoffs:
- back to the owning domain skill after persistence if more record work remains
- no handoff when persistence is the final step

## Trigger Signals

Use this skill when the user says things like:
- "save this for later"
- "make this persistent"
- "store this in the workspace"
- "save this on the project"
- "keep this as a task document"
- "create a reusable brief"
- "we should be able to use this later"
- "save this file so the team can refer back to it"

## Workflow

1. Resolve the workspace first when the target home is workspace, project, milestone, or task.
2. Decide whether the content belongs in:
   - VFS only
   - backend persistent file
   - a primary operational object such as a project update, task comment, or thread
3. If backend persistence is needed, choose the home using `home_type/home_id`.
4. Choose a stable path and filename for that home.
5. Read or search the backend file home first when a durable file may already exist.
6. Create, overwrite, edit, or move the file using the backend files API.
7. Verify the saved result with backend `read` or `info`.
8. Return a short summary in chat and keep the full document in the persistent backend file.

## Decision Rules

- Use VFS for:
  - temporary drafts
  - internal working memory
  - unstable pre-approval content
  - execution scaffolding during the current workflow
- Use backend persistent files for:
  - documents the user wants saved for later
  - documents intended for reuse or sharing
  - long-form artifacts attached logically to a user, workspace, project, milestone, or task
  - durable outputs of a completed workflow
- Do not use backend files for:
  - short task comments
  - short project updates
  - direct CRUD on project/task/milestone records
  - thread-like ongoing discussion
- Use this skill as the persistence step after planning or drafting, not as a replacement for the domain skill that owns the business workflow.
- Prefer `home_type/home_id` over legacy `project_id`, `milestone_id`, and `task_id`.
- Read first before overwrite when a persistent file may already exist.
- Prefer overwrite or edit for known durable paths instead of creating duplicates.

## Scope Routing

- **User file**
  - private drafts, personal notes, working documents not yet attached to team work
  - use `/v1/users/{user_id}/files`
  - include organization context when required by the user-home create flow
- **Workspace file**
  - cross-project plans, SOPs, resource plans, weekly operating plans, portfolio reviews
  - use `/v1/workspaces/{workspace_id}/files` with `home_type="workspace"` and `home_id={workspace_id}`
- **Project file**
  - project brief, status review, renewal plan, recovery plan, implementation plan
  - use `/v1/workspaces/{workspace_id}/files` with `home_type="project"` and `home_id={project_id}`
- **Milestone file**
  - phase brief, readiness review, acceptance checklist, handoff package
  - use `/v1/workspaces/{workspace_id}/files` with `home_type="milestone"` and `home_id={milestone_id}`
- **Task file**
  - execution brief, troubleshooting note, research memo, deep checklist
  - use `/v1/workspaces/{workspace_id}/files` with `home_type="task"` and `home_id={task_id}`

## Path Conventions

- **Workspace**
  - `/plans/resource-plan.md`
  - `/plans/weekly-assignment-plan.md`
  - `/reviews/portfolio-review-YYYY-MM-DD.md`
  - `/policies/<slug>.md`
- **Project**
  - `/briefs/project-brief.md`
  - `/reviews/status-review.md`
  - `/plans/action-plan.md`
  - `/client/client-summary.md`
- **Milestone**
  - `/phase-brief.md`
  - `/readiness-review.md`
  - `/acceptance-checklist.md`
- **Task**
  - `/execution-brief.md`
  - `/troubleshooting-note.md`
  - `/research-note.md`
- **User**
  - `/drafts/<slug>.md`
  - `/notes/<slug>.md`

## Scratchpad Contract

- Keep drafts in VFS or session files until the content is stable enough to persist.
- When backend persistence is used, record:
  - target home
  - chosen path
  - whether the operation was create, overwrite, edit, or move
  - verification result

## References Map

- Read `references/api.md` for real backend files endpoints and request shapes.
- Read `references/workflows.md` for the VFS-to-backend persistence flow.
- Read `references/gotchas.md` before overwriting, moving, or scoping files.

## Completion Criteria

- The agent chose the correct endpoint: VFS draft, backend file, or operational object.
- Persistent files were saved to the correct backend home when needed.
- Existing persistent files were reused or updated instead of duplicated when appropriate.
- The saved backend file was verified with a backend read or info check.
