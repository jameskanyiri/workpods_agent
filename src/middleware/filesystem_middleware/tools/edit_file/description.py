EDIT_FILE_TOOL_DESCRIPTION = """
Performs exact string replacements in files.

Usage:
- You must read the file before editing. This tool will error if you attempt an edit without reading the file first.
- When editing, preserve the exact indentation (tabs/spaces) from the read output. Never include line number prefixes in old_string or new_string.
- ALWAYS prefer editing existing files over creating new ones.
- Only use emojis if the user explicitly requests it.

## Display Name (`display_name`)

Use plain, action-oriented language. Never mention file names or paths.
Examples: "Updating", "Making changes", "Revising the document", "Applying corrections"
"""