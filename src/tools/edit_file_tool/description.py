
EDIT_FILE_TOOL_DESCRIPTION = """
Performs exact string replacements in files.

Usage:
- You must read the file before editing. This tool will error if you attempt an edit without reading the file first.
- When editing, preserve the exact indentation (tabs/spaces) from the read output. Never include line number prefixes in old_string or new_string.
- ALWAYS prefer editing existing files over creating new ones.
- Only use emojis if the user explicitly requests it.

You have access to two file systems:
1. **local** — for anything related to skills (references, templates, scripts, examples)
2. **vfs** — for workspace content (generated documents, project data, script outputs)

Use the `storage_type` parameter to select:
- storage_type="local" — edit in the local skills directory
- storage_type="vfs" (default) — edit in the virtual filesystem

Rule: Skills are always in local. Everything else is in VFS.
"""
