# Persistent Files Workflows

## Workflow 1: Draft In VFS, Then Persist

Use when the content is still evolving.

1. Draft or refine the content in VFS scratchpad files.
2. Decide whether the document should persist beyond the current run.
3. Resolve the target backend home.
4. Search or inspect the target backend path if duplication is possible.
5. Save with backend file create or overwrite.
6. Verify with backend read or info.
7. Return a short summary in chat.

## Workflow 2: Save New Durable File

Use when no persistent file exists yet.

1. Resolve target scope.
2. Choose stable path.
3. Optionally check for duplicates with `search` or `info`.
4. Create file with `POST /files`.
5. Verify with `GET /files/content`.

## Workflow 3: Update Existing Durable File

Use when the path is already part of an established workflow.

1. Read existing backend file first.
2. Decide between:
   - full overwrite
   - find/replace edit
   - move/rename
3. Apply the change.
4. Verify persisted result.

## Workflow 4: Scope Selection

Choose the narrowest durable home that matches later reuse.

- user: private working note
- workspace: cross-project artifact
- project: project-level artifact
- milestone: phase-level artifact
- task: execution-level artifact

If the content is only a short execution note or stakeholder checkpoint, prefer comment or project update instead of a backend file.
