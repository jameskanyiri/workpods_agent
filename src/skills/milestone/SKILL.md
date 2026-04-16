---
name: milestone
description: Triggered when the user wants to create, structure, review, or move forward milestones, phases, checkpoints, deliverables, or stage-based work. Also use when a project phase should become a milestone or when tasks need milestone linkage or milestone risk review. Do not use this as the first skill for renewal diagnosis or recovery triage when `commercial-lifecycle` is the better fit.
---

# Milestone Skill

## Purpose

Own milestone design, milestone creation, milestone status review, and milestone linkage strategy for tasks. This skill handles phase-to-milestone conversion and milestone risk framing. It does not own renewal diagnosis, recovery triage, or detailed task decomposition except where milestone structure depends on it.

Common incoming handoffs:
- `project` when a project request is really phase-shaped
- `project-execution` when the next structural move is a milestone
- `task` when broad task work should first become a milestone

Common outgoing handoffs:
- `task` when the milestone now needs actionable work
- `commercial-lifecycle` when the real problem is renewal, recovery, or follow-up
- `persistent-files` for durable milestone documents

## Trigger Signals

Use this skill when the user says things like:
- "create a milestone"
- "site assessment should be a milestone"
- "what milestone are we on"
- "is this phase on track"
- "link these tasks to a milestone"
- "what milestones are coming up"

Prefer `commercial-lifecycle` first when the user is really asking:
- how to renew an account
- how to reduce expired MC
- what account should be reactivated
- what the team should focus on next

## Workflow

1. Resolve workspace and target project.
2. Read:
   - milestone statuses
   - current project detail for existing milestones and tasks
3. Decide the operating mode:
   - direct action for simple milestone CRUD or linkage changes
   - draft-first for complex phase planning, readiness review, or multi-record milestone restructuring
   - document-only for milestone-scoped long-form documents such as phase briefs or acceptance checklists
4. Update `/.workpods-agent/projects/<project-slug>/milestones.md` when the flow needs milestone planning context.
5. For multi-step work, create todos before writes.
6. If the user is describing a phase, convert it into a milestone proposal with:
   - name
   - `start_date` and/or `end_date` (YYYY-MM-DD; the milestone API has no separate `target_date` field — see `references/api.md`)
   - definition of done
   - task grouping or follow-up task plan
7. Confirm before milestone creation or bulk task linkage.
8. Write the milestone or milestone update.
9. Verify linkage or current milestone state if the flow depends on it.

## Decision Rules

- Use milestones for phases, checkpoints, and deliverables; do not use them for single action items.
- If the project has no milestones and the user is already describing a phase, recommend creating the milestone before more tasks.
- A milestone should have a clear done condition and at least one task path toward completion.
- Do not default to a new milestone just because an account needs renewal or recovery. First decide whether the business move truly requires a new service period or delivery phase.
- Remember that `ACTIVE` is a milestone state, not a business outcome by itself.
- If tasks already exist, prefer linking them rather than recreating them.
- If the user is asking for a simple milestone edit, update the milestone directly instead of creating a milestone document.
- Use a milestone document only when the phase needs long-form planning, readiness review, acceptance criteria, or a handoff package.
- If the milestone document should persist for later reuse, read `persistent-files` and save it into the backend files API under the `milestone` home.
- If the next action becomes task execution, lifecycle triage, or durable document persistence, hand off to the owning skill before proceeding.

## Gotchas

- Milestone statuses are separate from task and project statuses.
- Tasks survive milestone deletion, so verify `milestone_id` linkage after updates that matter.
- Do not present milestone progress without reading both milestone and task state.
- A renewal bottleneck is often follow-up, ownership, billing, or stale dates rather than missing milestone structure.
- A milestone that is just one task is usually the wrong structure.
- Do not create a milestone document when a direct milestone update is sufficient.

## Scratchpad Contract

- Maintain `/.workpods-agent/projects/<project-slug>/milestones.md`.
- Save milestone-scoped long-form documents under `/.workpods-agent/projects/<project-slug>/milestones/<milestone-slug>/` when needed.
- Record:
  - milestone purpose
  - `start_date` and `end_date` (YYYY-MM-DD)
  - definition of done
  - related tasks or missing tasks
  - current risk or blockers

## References Map

- Read `references/api.md` for exact routes and status lookups.
- Read `references/workflows.md` for milestone-first structuring and task linkage.
- Read `references/gotchas.md` before status review or milestone writes.
- Read `../persistent-files/SKILL.md` when a durable milestone-scoped document is needed.
- Read `examples/site-assessment.md` for the phase-to-milestone pattern.
- Use `templates/milestone-plan.md` for scratchpad updates.

## Completion Criteria

- The milestone exists AND every attribute set during the request — internally verified against the API response for `name`, `status_id`, `start_date`, `end_date`, etc. — has been confirmed by reading the milestone back. A 200 response is not verification; the fields the agent intended to set must appear populated in the GET response.
- The user-facing report uses plain English, not API field names: "title", "status", "start date", "end date", "description" — never `name`, `status_id`, `start_date`, or backticked identifiers. Verify in schema vocabulary; communicate in project vocabulary.
- Any attribute the user mentioned but did not set is explicitly surfaced as a loose end in plain English (e.g., "you didn't give a start date — want one or leave it blank?"), not silently dismissed as "optional."
- Linked tasks are accounted for or the missing task gap is explicit.
- The milestone scratchpad is current.
- The user receives the next action needed to move the milestone or service period forward.
