---
name: project
description: Triggered when the user wants to create, structure, fix, move forward, or update a project, including setting dates, statuses, leads, members, metadata, scope, or starter milestones and tasks. Also use when a project write failed partially and needs verification or repair. Do not use this as the first skill for sales, renewal, recovery, or team-prioritization requests when `commercial-lifecycle` is the better fit.
---

# Project Skill

## Purpose

Own project setup and project record updates. This skill handles project creation, metadata updates, lead and member preparation, lifecycle status repair, date repair, and the recommendation of the next structural move after the project record exists. It does not own business triage, renewal strategy, recovery scoring, or deep milestone design or task decomposition beyond handing off cleanly to other skills.

Common incoming handoffs:
- `workspace` after context resolution
- `project-execution` when the next step is a project record change

Common outgoing handoffs:
- `commercial-lifecycle` when the real issue is business movement
- `milestone` when the work is phase-shaped
- `task` when the next move is actionable task work
- `persistent-files` when a project document should persist

## Trigger Signals

Use this skill when the user says things like:
- "create a new project"
- "set up this client project"
- "rename the project"
- "set the start date" / "set the end date" / "set the target date" (the API uses `start_date` and `end_date` — see `references/api.md`)
- "assign James as lead"
- "fix the project details"
- "what have we done on this project"
- any request to create or repair project-level records

Prefer `commercial-lifecycle` first when the user is really asking about:
- improving sales
- deciding the best next account to pursue
- reducing expired MC
- renewal prevention
- account reactivation
- team prioritization

## Workflow

1. Resolve the workspace first.
2. Read reference data before asking the user for missing project decisions:
   - project statuses
   - workspace members if lead or members matter
   - existing project detail if the request is an update or repair
3. Decide the operating mode:
   - direct action for simple project CRUD or repair
   - draft-first for complex project plans or multi-record follow-on work
   - document-only for reusable project briefs, reviews, or client-facing documents
4. Create or update:
   - `/.workpods-agent/sessions/<session-id>/plan.md` when the flow is multi-step
   - `/.workpods-agent/projects/<project-slug>/brief.md` when the flow needs a reusable project document
5. For 3+ tool flows, use `write_todos` before API writes.
6. Collect only the fields that materially affect the project write.
7. Confirm before creating or making multi-field updates.
8. Execute the project write.
9. Re-read the project if any important field could have failed to persist.
10. Save any reusable project-facing deliverable under `/.workpods-agent/projects/<project-slug>/` only when the workflow actually needs a document.
11. Recommend the next structural move immediately after success, usually a commercial next move, milestone design, or starter tasks depending on the bottleneck.

## Decision Rules

- If the user is describing a phase, checkpoint, or delivery stage, recommend a milestone instead of a broad task.
- If the request is to fix or confirm a project field, read the project first instead of asking the user to repeat what they already provided.
- If the request is really about business movement, lifecycle risk, renewal, recovery, or account prioritization, hand off to `commercial-lifecycle` before writing project metadata.
- Normalize relative dates to exact `YYYY-MM-DD` values before writing.
- Treat project status and dates (`start_date`, `end_date`) as support for business movement, not as the success condition by themselves.
- If a critical project field did not persist, treat the flow as incomplete and repair it after confirmation.
- If the user asks for a structured reusable output tied to the project, save it to a stable project file and respond in chat with a short summary.
- If the project document should persist beyond the current run, read `persistent-files` and save it into the backend files API under the `project` home.
- If the user is asking for a simple project edit, update the project directly and do not create a planning document.
- If the workflow is draft-first, summarize the proposed writes and ask for confirmation before applying related multi-record changes.
- If the next action stops being project metadata and becomes milestone, task, lifecycle, or durable-document work, hand off to the owning skill before proceeding.

## Gotchas

- Project create and update flows often need verification of saved dates and lead/member fields.
- Status ids must come from workspace project statuses; do not guess them.
- Do not treat project updates, milestones, or tasks as project metadata.
- Do not treat project metadata cleanup as the main goal when the business issue is follow-up, quote progression, renewal, or reactivation.
- If the project was created successfully but `start_date`, `end_date`, `lead_user_id`, or any other user-specified field did not persist, do not stop at "it created"; repair the record. The API silently drops unknown fields, so always GET the project back and confirm each intended field appears populated.

## Scratchpad Contract

- Maintain `/.workpods-agent/projects/<project-slug>/brief.md`.
- Save reusable project deliverables under `/.workpods-agent/projects/<project-slug>/` using stable names such as `project-brief.md`, `status-review.md`, `action-plan.md`, or `meeting-summary.md`.
- Record:
  - project objective and scope
  - exact `start_date` and `end_date` (YYYY-MM-DD)
  - lead and member decisions
  - status choice
  - known next structural move
- Read and revise the existing brief before creating a new one.

## References Map

- Read `references/api.md` for endpoints and payload notes.
- Read `references/workflows.md` for create, repair, and verification flow.
- Read `references/gotchas.md` before project writes that involve dates, statuses, or lead/member changes.
- Read `../persistent-files/SKILL.md` when the project workflow needs a durable backend file instead of a VFS-only draft.
- Read `examples/create-project.md` for a realistic project setup conversation.
- Use `templates/project-brief.md` when creating the project scratchpad.
- Use `scripts/normalize_relative_date.py` and `scripts/validate_project_create.py` when date or required-field validation is error-prone.

## Completion Criteria

- The project record exists or the requested project update is applied AND every attribute set during the request — internally verified against the API response for `name`, `status_id`, `start_date`, `end_date`, `lead_user_id`, `member_ids`, etc. — has been confirmed by reading the project back. A 200 response is not verification; the fields the agent intended to set must appear populated in the GET response.
- The user-facing report uses plain English, not API field names: "title", "status", "lead", "team members", "start date", "end date", "short summary" — never `name`, `status_id`, `lead_user_id`, `member_ids`, `summary`, or backticked identifiers. Verify in schema vocabulary; communicate in project vocabulary.
- Any attribute the user mentioned but did not set is explicitly surfaced as a loose end in plain English (e.g., "you didn't give an end date for the project — want one or leave it blank?"), not silently dismissed as "optional."
- The project brief scratchpad is current when a reusable project document was needed.
- The user has a concrete next recommended step grounded in project state and, when relevant, business stage.
