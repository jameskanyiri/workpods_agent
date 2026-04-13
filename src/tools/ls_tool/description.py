LIST_FILES_TOOL_DESCRIPTION = """Lists all files in a directory.

This is useful for exploring the filesystem and finding the right file to read or edit.
You should almost ALWAYS use this tool before using the read_file or edit_file tools.

You have access to two file systems:
1. **local** — for anything related to skills (references, templates, scripts, examples)
2. **vfs** — for workspace content (generated documents, project data, script outputs)

Use the `storage_type` parameter to select:
- storage_type="local" — read from the local skills directory
- storage_type="vfs" (default) — read from the virtual filesystem

Examples:
- ls(path="/", storage_type="local") — list all skills
- ls(path="payroll/references", storage_type="local") — list skill reference files
- ls(path="/") — list workspace root (VFS)
- ls(path="/acme-ltd/data") — list generated data in workspace (VFS)

Rule: Skills are always in local. Everything else is in VFS."""
