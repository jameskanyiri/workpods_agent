---
name: workspace
description: Triggered when the user wants to resolve the current workspace, confirm which workspace to use, list or switch workspaces, inspect workspace members, invite a member, or fetch workspace context before other project or task work. Also use when a request is blocked by an unknown workspace or missing member list.
---

# Workspace Skill

## Purpose

Own workspace resolution and workspace context setup for downstream workflows. This skill handles default workspace lookup, workspace listing, member lookup, and member-oriented confirmation. It also provides the scope context for workspace-level documents such as resource plans, weekly team plans, and portfolio reviews. It does not own project creation, task execution, or milestone design beyond supplying the workspace context those workflows need.

Common incoming handoffs:
- direct user requests that need workspace resolution
- any workflow blocked by missing workspace or member context

Common outgoing handoffs:
- `project` for project record work
- `task` for task execution work
- `milestone` for phase structure
- `commercial-lifecycle` for sales, renewal, recovery, or prioritization
- `persistent-files` when a workspace document should persist

## Trigger Signals

Use this skill when the user says things like:
- "which workspace am I in"
- "use my default workspace"
- "show workspace members"
- "switch to another workspace"
- "who can I assign this to"
- "invite this person"
- any project or task request where `workspace_id` is missing or the member list is required before a write

## Workflow

1. Resolve the workspace before any downstream workflow if the active workspace is missing or ambiguous.
2. Read first:
   - `GET /v1/workspaces/default` for the default workspace
   - `GET /v1/workspaces` only if the user needs a different workspace
   - `GET /v1/workspaces/{workspace_id}/members` when assignees, leads, or invites matter
3. For multi-step work, create or update session notes under `/.workpods-agent/sessions/<session-id>/`.
4. Ask only for the one missing decision that blocks the next action.
5. Confirm only when switching context materially changes which records will be read or written.
6. After resolving the workspace, hand off to the domain skill that owns the next step.
7. If the next step changes object type or responsibility, read the next skill before proceeding.

## Decision Rules

- Resolve workspace first if any downstream API write depends on it.
- If the user names a person for assignment or lead selection, fetch members before asking follow-up questions.
- If the request is otherwise clear, do not ask the user to restate workspace information that can be read from the API.
- Workspace-scoped documents are appropriate for cross-project planning, strategy, staffing, and portfolio review. Do not use them for simple project, task, or milestone edits.
- When a workspace document should persist for later reuse, read `persistent-files` and save it into the backend files API under the `workspace` home instead of leaving it only in VFS.
- Once workspace context is resolved, do not keep control of the workflow if another skill clearly owns the next action.

## Gotchas

- `GET /v1/workspaces/default` returns one workspace object, not a list.
- Workspace writes are rare and should be treated as separate from project/task workflows.
- Do not guess that a named person is a workspace member; read members first.
- If the user wants another workspace, list choices before proceeding with project or task writes.

## Scratchpad Contract

- Read or create `/.workpods-agent/sessions/<session-id>/working-notes.md` for workspace resolution notes.
- Save reusable workspace-level documents under `/.workpods-agent/workspaces/<workspace-id>/` when the downstream workflow is draft-first or document-only.
- Record:
  - active workspace name and id
  - whether the workspace was user-selected or defaulted
  - member lookup results that affect later assignment or lead decisions
- Revise existing notes instead of creating duplicates.

## References Map

- Read `references/api.md` for exact endpoints and payload notes.
- Read `references/workflows.md` when the request needs workspace resolution before another skill.
- Read `references/gotchas.md` if member identity or workspace switching is causing ambiguity.
- Read `../persistent-files/SKILL.md` when the workflow needs a durable workspace document.
- Read `examples/member-resolution.md` for a concrete member lookup flow.
- Use `templates/session-context.md` when creating or refreshing a session note.

## Completion Criteria

- The active workspace is resolved or the blocking ambiguity is clearly presented to the user.
- Required member context is available when downstream work depends on it.
- Session scratchpad notes reflect the current workspace context.
