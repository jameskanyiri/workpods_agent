WRITE_FILE_TOOL_DESCRIPTION = """Writes to a new file in the filesystem.

Usage:
- The write_file tool will create a new file.
- Prefer to edit existing files (with the edit_file tool) over creating new ones when possible.

You have access to two file systems:
1. **local** — for anything related to skills (references, templates, scripts, examples)
2. **vfs** — for workspace content (generated documents, project data, script outputs)

Use the `storage_type` parameter to select:
- storage_type="local" — write to the local skills directory
- storage_type="vfs" (default) — write to the virtual filesystem

Examples:
- write_file(file_path="payroll/data/notes.md", content="...", storage_type="local") — write a skill file
- write_file(file_path="/acme-ltd/reports/vat_return_march.md", content="...") — write a report to VFS

Rule: Skills are always in local. Everything else is in VFS.
"""
