READ_FILE_TOOL_DESCRIPTION = """
Reads a file from the filesystem.

This tool reads from two sources automatically:
1. **Workspace files** — generated documents, project data, and script outputs stored in the virtual filesystem
2. **Skill files** — SKILL.md files and supporting references from the skills directory on disk

The tool checks the workspace first, then falls back to disk for skill files. You do not need to specify which source — just provide the file path.

Usage:
- By default, it reads up to 100 lines starting from the beginning of the file
- **IMPORTANT for large files**: Use pagination with offset and limit parameters to avoid context overflow
  - First scan: read_file(file_path, limit=100) to see file structure
  - Continue: read_file(file_path, offset=100, limit=200) for next 200 lines
- Results are returned with line numbers starting at 1
- You should ALWAYS make sure a file has been read before editing it.
- For skill files, use `limit=1000` since the default of 100 lines is too small for most SKILL.md files.

Examples:
- read_file(file_path="/data/trial_balance.json") — read generated data from workspace
- read_file(file_path="/Users/.../skills/payroll/SKILL.md", limit=1000) — read a full skill file from disk

## Display Name (`display_name`)

Use plain, action-oriented language. Never mention file names, paths, or extensions.
Examples: "Reading", "Reviewing the document", "Checking the details", "Loading instructions"
"""
