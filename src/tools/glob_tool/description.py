GLOB_TOOL_DESCRIPTION = """Find files matching a glob pattern.

Supports standard glob patterns: `*` (any characters), `**` (any directories), `?` (single character).
Returns a list of file paths that match the pattern.

You have access to two file systems:
1. **local** — for anything related to skills (references, templates, scripts, examples)
2. **vfs** — for workspace content (generated documents, project data, script outputs)

Use the `storage_type` parameter to select:
- storage_type="local" — search the local skills directory
- storage_type="vfs" (default) — search the virtual filesystem

Examples:
- glob(pattern="payroll/**/*.md", storage_type="local") — find all markdown files in a skill
- glob(pattern="**/*.json") — find all JSON files in VFS

Rule: Skills are always in local. Everything else is in VFS."""
