---
name: comments
description: Triggered when the user wants to add, revise, review, or delete a task comment, execution note, handoff note, follow-up note, or short work log tied to a specific task.
---

# Comments Skill

## Purpose

Own task comments and task-level execution notes. This skill is for short operational notes tied to one task. It does not own project-wide updates or broader discussion threads.

Common incoming handoffs:
- `task` when the work resolves to a short task note

Common outgoing handoffs:
- `project-updates` for project-level communication
- `threads` for broader ongoing discussion
- `persistent-files` only if the user actually needs a durable long-form task document

## Trigger Signals

Use this skill when the user says things like:
- "comment on this task"
- "leave a note"
- "log this blocker on the task"
- "what comments are on this task"
- "edit the comment"

## Agent-Initiated Triggers

The agent should also activate this skill **without being asked** when an event in the conversation
just generated information the task record itself doesn't carry:

- A meaningful task just completed AND something concrete was delivered, learned, or unblocked
  ("8 workflows mapped, 3 flagged as pilot candidates", not "task done")
- A blocker on a task just cleared (assignee added to a stalled task, status moved out of
  "blocked", missing dependency resolved) — log what unblocked it
- A decision was made in chat that lives nowhere on the task record ("we're going with the
  consulting firm", "out of scope for this task: mobile") — capture it on the right task

**Skip when:**
- The status change alone tells the story (the activity log already captured `task.status_changed`)
- There's no new content beyond "task done" — that's a tautology, not a comment
- The moment is project-scope or stakeholder-relevant, not task-scope. In that case post a
  *project update* instead and reference the task inside it. Don't double-post a comment plus an
  update for the same event.

**Approval pattern: comments are auto.** State in plain English what you'll write before posting,
then post it, then confirm it landed. Don't ask permission for every comment — but do show the
draft text so the user can intercept if it's wrong.

## Workflow

1. Resolve workspace, project, and task.
2. Read task detail or task comments first.
3. If adding a comment, keep it specific to execution state, blocker, handoff, or evidence.
4. Confirm before destructive comment edits or deletes if the user intent is not explicit.
5. Post or update the comment.

## Decision Rules

- Use comments for task-level execution details.
- If the note affects the whole project or is stakeholder-facing, recommend a project update instead.
- Keep comments concise and action-oriented.
- Do not create a task document for a short blocker note, work log, or handoff note.
- If the user needs substantial long-form guidance, recommend a task-scoped document instead of overloading a comment.
- If the note stops being a short task-level comment, hand off to the skill that owns the broader object.

## Gotchas

- Do not store project-level status only as a task comment if it belongs on the project.
- Read existing comments before claiming there are none or before editing.
- Keep comment content tied to the task, not general chat.

## Scratchpad Contract

- If the comment is being drafted as part of a larger flow, keep the draft in the session working notes before posting.

## References Map

- Read `references/api.md` for comment CRUD routes.
- Read `references/workflows.md` for add/update/delete flow.
- Read `references/gotchas.md` before choosing between a comment and a project update.
- Read `examples/task-comment.md` for a practical task note.
- Use `templates/comment.md` when drafting a comment before posting.

## Completion Criteria

- The comment is posted, updated, deleted, or accurately summarized.
- The note is correctly placed at the task level rather than hidden in chat.
