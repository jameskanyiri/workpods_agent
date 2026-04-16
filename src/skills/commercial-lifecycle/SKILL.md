---
name: commercial-lifecycle
description: Triggered when the user wants to improve sales, reduce expired accounts, increase warranty-to-MC conversion, reactivate clients, prioritize the team, or decide the best next business move for one project or across the workspace.
---

# Commercial Lifecycle Skill

## Purpose

Own business progression across Ecocycle's workspace. This skill handles lead progression, proposal follow-up, warranty-to-MC conversion, MC renewal prevention, expired-client recovery, and team prioritization. It decides the best commercial or retention move before any project, milestone, task, or update write happens.

Common incoming handoffs:
- `workspace` after context resolution
- `project` or `project-execution` when the real issue is business movement

Common outgoing handoffs:
- `task` when the next move becomes clear actionable work
- `project-updates` when the outcome should be posted on the project
- `persistent-files` when the review or plan should persist
- `project` or `milestone` only when the business move truly requires those writes

## Trigger Signals

Use this skill when the user says things like:
- "how do we improve sales"
- "why are clients not subscribing"
- "which projects should we focus on"
- "how do we reduce expired MC"
- "move this account forward"
- "which client should we pursue next"
- "how do we convert warranty clients"
- "what should the team work on this week"
- "which accounts are worth reactivating"

## Workflow

1. Resolve workspace and, if relevant, target project or shortlist.
2. Read the current lifecycle context:
   - project statuses
   - task statuses
   - milestone statuses when service periods matter
   - project detail, tasks, milestones, updates, and labels
3. Classify the account or list into one of these business pipelines:
   - sales pipeline: `LEAD`, `SITE ASSESSMENT`, `PROPOSAL SENT`
   - active delivery/service: `ONGOING`, `ONCALL`
   - retention/protection: `UNDER WAR`, `FREE MC`, `CURRENT MC`
   - recovery/leakage: `EXPIRED WAR`, `EXPIRED MC`
   - closed: `CANCELLED`, `LOST LEAD`, `SYSTEM DECOMMISSIONED`
4. Identify the business objective:
   - qualify
   - close
   - deliver
   - convert to MC
   - renew
   - reactivate
   - deprioritize
5. Identify the real bottleneck:
   - no decision-maker
   - no quote or proposal
   - no follow-up
   - no renewal action
   - stale contract dates
   - no owner
   - missing client-response step
   - missing service evidence
6. Recommend the single best business move first.
7. Decide the operating mode:
   - direct action for simple, low-ambiguity record changes
   - draft-first for multi-record coordination, approval-heavy changes, and reusable planning documents
   - document-only for knowledge artifacts and shareable plans that should not mutate records yet
8. Only then create or update the smallest useful set of tasks, milestones, project fields, or updates.
9. Verify critical writes when the workflow includes them.

## Decision Rules

- Treat project statuses as lifecycle signals, not the goal by themselves.
- Use project labels like system size and location to rank account upside and field efficiency.
- Use task labels like `follow-up`, `site-assessment`, `mc-renewal`, `warranty`, `maintenance`, `billing`, `reporting`, `service-check`, `spot-check`, and `on-call` to map the next action to the correct operating motion.
- For `PROPOSAL SENT`, default toward follow-up and close planning before internal restructuring.
- For `UNDER WAR`, default toward conversion planning before warranty expiry.
- For `CURRENT MC`, default toward renewal prevention, service continuity, billing visibility, and expiry-risk management.
- For `EXPIRED MC`, default toward reactivation scoring before assuming the account should remain dormant.
- For `CANCELLED`, `LOST LEAD`, and `SYSTEM DECOMMISSIONED`, do not treat them as active opportunities unless the user explicitly wants a reactivation strategy.
- Only create a new milestone when the business move truly needs a new tracked delivery phase or service period.
- Only create tasks after the commercial bottleneck is clear.
- Once the bottleneck is clear, hand off to the skill that owns the next concrete write instead of keeping the entire workflow here.

## Default Outputs

When the user is asking for advice or triage, prefer outputs like:
- best next account to pursue
- accounts at highest risk of expiry
- accounts most likely to renew
- accounts most worth reactivating
- top actions for the team this week
- the single best next move for a named account

When those outputs are substantial or intended for reuse:
- save workspace-wide deliverables under `/.workpods-agent/workspaces/<workspace-id>/`
- save single-account deliverables under `/.workpods-agent/projects/<project-slug>/`
- use stable markdown filenames such as `resource-plan.md`, `renewal-analysis.md`, `reactivation-priority.md`, or `team-focus-weekly.md`
- return a short summary in chat instead of the full document unless the user explicitly asks for inline content
- when the document should persist beyond the current run, read `persistent-files` and save it into the backend files API using the correct `workspace` or `project` home

When the user is asking to act on the portfolio rather than just review it:
- do not stop at document creation
- summarize the exact proposed writes after the draft
- ask for confirmation before multi-record project, task, milestone, or update changes
- apply the writes after approval and verify persisted state

## Gotchas

- Do not equate a status change with real business progress.
- Do not create busy tasks that are not tied to a real bottleneck.
- Do not flatten all accounts into the same advice; use lifecycle stage, system size, and location.
- Do not jump to milestone creation for renewal or recovery when follow-up, ownership, or billing is the real problem.
- Do not call an account healthy just because it is `CURRENT MC` or `UNDER WAR` if dates are stale or no next action exists.
- Do not create a workspace document for simple project, task, or milestone edits that should be executed directly.

## Scratchpad Contract

- Maintain `/.workpods-agent/sessions/<session-id>/plan.md` for multi-step triage and execution.
- Save reusable workspace-level outputs under `/.workpods-agent/workspaces/<workspace-id>/`.
- When focused on a single account, update the relevant project files under `/.workpods-agent/projects/<project-slug>/`.
- Record:
  - lifecycle stage
  - business objective
  - bottleneck
  - recommended next move
  - any supporting writes required

## Completion Criteria

- The account or workspace view has a clear business-stage diagnosis.
- The primary bottleneck is explicit.
- The user receives the highest-value next move, not just administrative cleanup.
- If writes were necessary, they are the smallest set that genuinely supports sales, retention, recovery, or execution.
- If draft-first mode was used, the proposed writes are explicit and confirmation was requested before applying them.
