---
name: project-execution
description: Triggered when the user wants the agent to move a project forward across multiple objects, such as project -> milestone -> task -> update, or when the agent should decide the right next structure instead of handling only one isolated write. For sales, renewal, recovery, or team-focus requests, consult `commercial-lifecycle` first.
---

# Project Execution Skill

## Purpose

Own multi-entity execution flows that span project, milestone, task, and update work. This skill orchestrates other local skills and decides the best structural next move. It is the main workflow skill for "move this forward" requests after the business bottleneck is understood.

Common incoming handoffs:
- direct user requests to move a project forward
- `workspace` after context resolution for a multi-object workflow

Common outgoing handoffs:
- `project`, `milestone`, `task`, or `project-updates` depending on the next object
- `commercial-lifecycle` when the real issue is sales, renewal, recovery, or prioritization
- `persistent-files` when the flow ends with a durable artifact

## Trigger Signals

Use this skill when the user says things like:
- "move this project forward"
- "set this up properly"
- "what should we create next"
- "complete the setup"
- "take this as far as you can"

## Workflow

1. Resolve workspace and target project context.
2. Read current project, milestone, task, member, and status context needed for the flow.
3. Create or refresh:
   - `/.workpods-agent/sessions/<session-id>/plan.md`
   - relevant project scratchpad files
4. Decide the correct structure:
   - commercial or lifecycle next move
   - project metadata
   - milestone(s)
   - task set
   - update
   - durable document if the workflow needs a persistent artifact
5. Use `write_todos` for multi-step work.
6. Confirm before creating or updating multiple records.
7. Execute in dependency order.
8. Verify critical writes.
9. Finish with the next best recommendation if more work remains.

## Decision Rules

- If the project record does not exist, create or repair it first.
- If the user is asking about sales progression, renewal, recovery, or team prioritization, use `commercial-lifecycle` to identify the bottleneck before choosing the object hierarchy.
- If the project phase is described but not structured, create or recommend a milestone before large task sets.
- If the work has progressed and should be visible to stakeholders, recommend or create a project update.
- If the workflow produces a durable document artifact, read `persistent-files` and persist it to the correct backend home instead of leaving it only in VFS.
- Always prefer the smallest set of writes that genuinely moves the project forward.
- Do not hold ownership longer than needed. Once the next object is clear, hand off to the skill that owns that object.

## Gotchas

- Do not jump straight to tasks if the project phase should first become a milestone.
- Do not jump straight to milestones or tasks if the real issue is follow-up, quote progression, renewal risk, stale dates, or missing ownership.
- Do not stop after partial success when the next fix is clear and low-risk after confirmation.
- Do not ask the user to restate information already available in project state or scratchpad notes.

## Scratchpad Contract

- Maintain the session plan and relevant project files under `/.workpods-agent/`.
- Record structure decisions, pending writes, verification results, and the next proposed move.

## References Map

- Read `references/workflows.md` for orchestration order.
- Read `references/gotchas.md` when choosing between objects.
- Read `../persistent-files/SKILL.md` when the flow should end with a durable backend file.
- Read `examples/move-project-forward.md` for a realistic multi-step flow.
- Use `templates/execution-plan.md` for session planning.

## Completion Criteria

- The project has moved to a more executable state.
- The right object hierarchy exists or the exact blocker is clear.
- The next best step is explicit and grounded in current state.
