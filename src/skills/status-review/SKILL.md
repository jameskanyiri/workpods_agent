---
name: status-review
description: Triggered when the user wants a status review, progress check, blocker audit, health summary, risk scan, "what's next" answer, or milestone-aware project health readout grounded in current workspace data.
---

# Status Review Skill

## Purpose

Own project health review, blocker detection, milestone-aware status synthesis, and next-step recommendation. This skill is a runbook for reading current state before advising. It does not own record creation except when the user explicitly asks to post the outcome somewhere.

Common incoming handoffs:
- direct user requests for project health or progress review
- `project` or `project-execution` when a read-first assessment is needed

Common outgoing handoffs:
- `project-updates` when the review should be posted
- `persistent-files` when the review should persist as a durable document

## Trigger Signals

Use this skill when the user says things like:
- "what have we done"
- "what's next"
- "give me the status"
- "what's blocked"
- "are we on track"
- "review this project's progress"

## Workflow

1. Resolve workspace and project.
2. Read project detail, milestones, tasks, and recent activity or updates when needed.
3. Summarize in this order:
   - blockers and overdue work
   - milestone risk
   - progress made
   - next concrete move
4. If the user wants a reusable artifact, save or update it under `/.workpods-agent/projects/<project-slug>/`, using `execution-log.md` or another stable document name such as `status-review.md`.
5. If the review should become a project update, hand off to `project-updates`.
6. If the review should persist beyond the current run, read `persistent-files` before treating it as complete.

## Decision Rules

- Read current state first. Never answer from memory.
- Use milestones and tasks together; do not review them in isolation.
- Lead with blocked, overdue, or high-risk work.
- Finish with one specific next recommendation.
- If the next action becomes posting, commenting, or durable persistence, hand off to the owning skill before proceeding.

## Gotchas

- Do not give optimistic summaries that hide blockers.
- Do not summarize stale state without reading the project first.
- Do not stop at counts; name the key item or missing structure that matters.

## Scratchpad Contract

- Maintain `/.workpods-agent/projects/<project-slug>/execution-log.md` for execution history and `/.workpods-agent/projects/<project-slug>/status-review.md` for reusable review deliverables when the review should persist beyond chat.
- Record:
  - review date
  - blockers
  - milestone risk
  - next recommendation

## References Map

- Read `references/api.md` for the main project and activity endpoints.
- Read `references/workflows.md` for the review order.
- Read `references/gotchas.md` before giving advice.
- Read `examples/james-residence.md` for a realistic summary pattern.
- Use `templates/status-review.md` for a saved report.
- Use `scripts/render_status_review.py` to render a concise markdown report from structured findings.

## Completion Criteria

- The review is grounded in current project state.
- The response names blockers or risks first when they exist.
- The user gets one concrete next step.
