# Persistent Files Gotchas

- All paths must be absolute and start with `/`.
- Directory paths must end with `/`.
- File paths must not end with `/`.
- Parent directories are auto-created by the backend.
- Path uniqueness is per home scope, so the same path can exist in different homes.
- Prefer `home_type/home_id` over legacy scope fields.
- Milestone and task homes must still be consistent with the workspace and project context.
- Default MIME type is `text/markdown`.
- Read before overwrite when a persistent file may already exist.
- Prefer overwrite or edit for known durable files instead of creating duplicates.
- Do not store short comments, short project updates, or direct CRUD outputs as backend files.
- User-home files are private by default.
- Creating user-home files may require organization context in addition to the user home route.
- Workspace/project/milestone/task file operations require workspace-level file permissions.
