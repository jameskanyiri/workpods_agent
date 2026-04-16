---
name: project-updates
description: Triggered when the user wants to post, draft, revise, summarize, or review a project update, progress note, stakeholder update, checkpoint summary, or client-facing project progress message, including renewal, reactivation, and commercial-decision updates that belong on the project record.
---

# Project Updates Skill

## Purpose

Own project-level progress updates. This skill drafts and posts updates that belong on the project record. It is also the right place for renewal, reactivation, and client-decision summaries once the facts are known. It does not own task comments or broader free-form discussion threads.

Common incoming handoffs:
- `status-review` when a review should be posted
- `commercial-lifecycle` when the business outcome should be recorded on the project

Common outgoing handoffs:
- `persistent-files` if the content becomes a durable project document instead of a short update
- `threads` if the user wants broader ongoing discussion rather than a checkpoint update

## Trigger Signals

Use this skill when the user says things like:
- "post an update"
- "give the project update"
- "draft a progress note"
- "summarize progress for the client"
- "what update should we add"
- "record the renewal outcome"
- "summarize the reactivation decision"

## Agent-Initiated Triggers

The agent should also activate this skill **without being asked** when an event in the conversation
crosses into stakeholder-relevant territory the project record alone doesn't communicate:

- A milestone just hit done — this is exactly what project updates exist for; capture what was
  completed, what it unblocks, and what's next
- A project's lifecycle status just changed (e.g., LEAD → SITE ASSESSMENT, UNDER WAR → CURRENT MC,
  PROPOSAL SENT → ONGOING) — name the change and the next move
- A multi-record setup just completed (e.g., a new milestone plus several starter tasks were
  created in one flow) — summarize the new structure for stakeholders so they understand the shape
- A stakeholder-relevant decision was made in chat that lives nowhere on the records ("we're going
  with the consulting firm", "moved the deadline to end of quarter", "scope reduced to mobile only")
- A task completion that is also milestone-significant or stakeholder-relevant — post the update at
  the higher scope and reference the task inside it. Don't double-post a comment AND an update.

**Skip when:**
- The change is task-local execution detail (use `comments` instead)
- The change is broader open-ended discussion (use `threads` instead)
- The structural fact is captured by the activity log and there's no new context to add. Vague
  posts ("good progress", "things are moving") are noise — every update must cite something
  concrete.

**Approval pattern: updates are draft → confirm → post.** Project updates are stakeholder-facing
and posted under the user's identity. Always draft the update, present it to the user, wait for
explicit approval, then post, then verify it landed. Never auto-post an update.

## Workflow

1. Resolve workspace and project.
2. Read project detail and, if needed, recent updates or activity.
3. Draft the update in `/.workpods-agent/projects/<project-slug>/updates-drafts.md`.
4. Distill:
   - what changed
   - current blockers
   - next actions
5. Confirm before posting.
6. Create or update the project update.
7. If the user only wanted a draft, keep it in project files and present a short summary for approval instead of pasting the full draft in chat.

## Decision Rules

- Use a project update for project-level progress or stakeholder communication.
- Use a project update when the team needs a durable account summary for renewal, reactivation, quote progression, or client decision state.
- If the content is only about one task's execution detail, prefer a task comment.
- Keep updates factual and grounded in current project state.
- Prefer saving reusable drafts in project files before presenting them in chat.
- Do not create a project document when the right object is a short project update.
- If the content becomes a long-form review, plan, or reusable artifact, hand off to `persistent-files` or the owning document-producing skill instead of forcing it into an update.

## Gotchas

- Do not post vague updates that are not backed by project state.
- Updates are project-scoped; do not confuse them with task comments.
- If the user asks for a client-facing summary, remove internal-only phrasing unless they ask otherwise.
- If the content becomes a long-form plan, review, or brief, treat that as a project document instead of forcing it into a project update.

## Scratchpad Contract

- Maintain `/.workpods-agent/projects/<project-slug>/updates-drafts.md`.
- Store:
  - draft text
  - evidence notes
  - open review points

## References Map

- Read `references/api.md` for update CRUD routes.
- Read `references/workflows.md` for draft/post flow.
- Read `references/gotchas.md` before posting a stakeholder-facing update.
- Read `examples/progress-update.md` for a practical update structure.
- Use `templates/project-update.md` for drafts.
- Use `scripts/render_update.py` to normalize a concise markdown update from structured fields.

## Completion Criteria

- The requested update is drafted or posted.
- The update content is grounded in current state.
- Scratchpad drafts are current if the update is not yet posted.
