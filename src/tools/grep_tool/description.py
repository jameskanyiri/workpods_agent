GREP_TOOL_DESCRIPTION = """Search for a text pattern across files.

Searches for literal text (not regex) and returns matching files or content based on output_mode.
Special characters like parentheses, brackets, pipes, etc. are treated as literal characters, not regex operators.

You have access to two file systems:
1. **local** — for anything related to skills (references, templates, scripts, examples)
2. **vfs** — for workspace content (generated documents, project data, script outputs)

Use the `storage_type` parameter to select:
- storage_type="local" — search the local skills directory
- storage_type="vfs" (default) — search the virtual filesystem

Examples:
- grep(pattern="vat_rate", storage_type="local") — search all skill files
- grep(pattern="paye", glob="payroll/**/*.md", storage_type="local") — search within a skill
- grep(pattern="TODO", output_mode="content") — search VFS with matching lines

Rule: Skills are always in local. Everything else is in VFS."""
