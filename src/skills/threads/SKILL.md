---
name: threads
description: Triggered when the user wants to create, inspect, update, archive, attach, or detach a discussion thread, project conversation, or ongoing discussion context, especially when the note is broader than a single task comment.
---

# Threads Skill

## Purpose

Own workspace threads and project-thread association. Use this skill for broader discussion context that should live with a project or remain as an ongoing thread. It does not own project updates or task comments.

Common incoming handoffs:
- `comments` or `project-updates` when the content is broader than those objects
- direct user requests for ongoing project discussion context

Common outgoing handoffs:
- `project-updates` when the content should be a stakeholder checkpoint
- `comments` when the note is really task-local
- `persistent-files` when the user needs a structured reusable artifact instead of a discussion thread

## Trigger Signals

Use this skill when the user says things like:
- "create a thread"
- "attach this conversation to the project"
- "show project threads"
- "remove the thread from the project"
- "archive this thread"

## Workflow

1. Resolve workspace and, if relevant, the target project.
2. Read existing thread or project-thread context first.
3. Decide whether the content belongs in:
   - a thread
   - a project update
   - a task comment
4. Confirm before creating, attaching, detaching, or deleting threads.
5. Execute the thread or project-thread action.

## Decision Rules

- Use a thread for broader discussion that spans multiple tasks or continues over time.
- Use a task comment for a one-task execution note.
- Use a project update for a stakeholder-facing progress checkpoint.
- Use a document instead of a thread only when the user needs a reusable, structured artifact such as a plan, brief, or review.
- If the content stops being ongoing discussion and becomes a document or checkpoint, hand off to the owning skill before proceeding.

## Gotchas

- Do not confuse project-thread association with task comments.
- A task may carry `thread_id`, but thread lifecycle is separate from task lifecycle.
- If the user wants ongoing project discussion context, prefer a project-linked thread over a comment.

## Scratchpad Contract

- Record thread linkage decisions in the session working notes when they affect later project or task work.

## References Map

- Read `references/api.md` for thread CRUD and project-thread routes.
- Read `references/workflows.md` for choosing between threads, comments, and updates.
- Read `references/gotchas.md` before attaching or detaching a thread.
- Read `examples/project-thread.md` for a project-linking example.

## Completion Criteria

- The thread decision is correct and the requested thread action is complete.
- The user has the right communication object for the job.
