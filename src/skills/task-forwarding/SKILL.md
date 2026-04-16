---
name: task-forwarding
description: Triggered when the user wants the agent to move a task or workstream forward, identify blockers, find the next action, unblock progress, sequence dependencies, or recommend the next unblocked step instead of just summarizing current state.
---

# Task Forwarding Skill

## Purpose

Own "move this forward" behavior at the task and workstream level. This skill identifies blockers, next actions, dependencies, and the smallest execution step that meaningfully advances the work.

## Trigger Signals

Use this skill when the user says things like:
- "move this task forward"
- "what's blocking this"
- "what should happen next"
- "unblock this"
- "what can we do right now"

## Workflow

1. Resolve workspace, project, and relevant task context.
2. Read current task, milestone, and project state.
3. Identify:
   - explicit blocker
   - missing dependency
   - next unblocked task
4. Update the task breakdown or session working notes.
5. If a concrete write is needed and safe, hand off to the owning skill after confirmation.
6. End with the next best move, not just a diagnosis.

## Decision Rules

- Prefer the next unblocked action over generic advice.
- If the task is too broad, break it down.
- If the blocker is missing structure, recommend the needed milestone, task, label, comment, or update.

## Gotchas

- Do not answer with abstract productivity advice when workspace state reveals a concrete next move.
- Do not hide a blocker behind a status summary.
- Read the current task/project first.

## Scratchpad Contract

- Record blockers, dependencies, and next actions in the task breakdown or session notes.

## References Map

- Read `references/workflows.md` for blocker analysis.
- Read `references/gotchas.md` before giving next-step guidance.
- Read `examples/unblock.md` for a simple unblock pattern.
- Use `templates/blocker-log.md` when recording blocker analysis.

## Completion Criteria

- The blocker is identified or ruled out.
- A specific next action is proposed.
- Relevant scratchpad notes are updated.
