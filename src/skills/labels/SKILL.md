---
name: labels
description: Triggered when the user wants to create, rename, organize, scope, apply, or review labels or label categories, including project-only, task-only, and milestone-aware tagging strategies for later filtering and reporting.
---

# Labels Skill

## Purpose

Own label categories, label definitions, entity scopes, and label application strategy. This skill explains when labels add value and helps apply them consistently. It does not replace status or priority management.

## Trigger Signals

Use this skill when the user says things like:
- "create a label"
- "set up categories"
- "tag these tasks"
- "make a project-only label"
- "how should we organize labels"
- "filter by label"

## Workflow

1. Resolve workspace and any target project/task context.
2. Read current labels and label categories before proposing new ones.
3. Update scratchpad notes if the labeling strategy is part of a larger project setup.
4. If new labels are needed, define:
   - category
   - entity scope
   - practical use case
5. Confirm before creating or modifying labels.
6. Apply labels to tasks only when the workflow needs real categorization beyond status or priority.

## Decision Rules

- Prefer status and priority when they already express the decision clearly.
- Use labels for cross-cutting filters like site, team, client stream, risk type, or dependency type.
- Keep labels sparse and useful; avoid creating near-duplicates.
- Use entity scopes intentionally so later filtering stays clean.

## Gotchas

- Read existing labels first to avoid duplicates.
- Entity scopes matter; do not promise a label is universal if it is scoped.
- Labels are useful for retrieval and reporting, not as a substitute for status.
- Do not add labels just to compensate for unclear task titles.

## Scratchpad Contract

- Record label strategy inside the relevant project brief or task breakdown when labels are part of execution planning.
- Note:
  - category names
  - label purpose
  - entity scope
  - where each label should be applied

## References Map

- Read `references/api.md` for label and category endpoints.
- Read `references/workflows.md` for label strategy and application flow.
- Read `references/gotchas.md` before creating new labels.
- Read `examples/label-strategy.md` for a practical setup.
- Use `templates/label-plan.md` when drafting a label scheme.

## Completion Criteria

- The label decision is clear and non-duplicative.
- Required categories or labels exist or are ready for confirmation.
- The user understands whether labels add value beyond current status/priority fields.
