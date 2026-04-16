GLOB_TOOL_DESCRIPTION = """
Find files matching a glob pattern.

Searches virtual filesystem state first. If no matches are found, falls back to searching the skills directory on disk.

Supports standard glob patterns: `*` (any characters), `**` (any directories), `?` (single character).
Returns a list of file paths that match the pattern.

Examples:
- `**/*.py` - Find all Python files
- `*.txt` - Find all text files in root
- `**/*.md` - Find all markdown files (including skill references)
- `**/SKILL.md` - Find all skill definition files

## Display Name (`display_name`)

Use plain, action-oriented language. Never mention glob patterns or file extensions.
Examples: "Looking up", "Finding documents", "Searching for relevant files"
"""