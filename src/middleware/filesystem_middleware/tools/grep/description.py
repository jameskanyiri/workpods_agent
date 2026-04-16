GREP_TOOL_DESCRIPTION = """
Search for a text pattern across files.

Searches for literal text (not regex) and returns matching files or content based on output_mode.
Special characters like parentheses, brackets, pipes, etc. are treated as literal characters, not regex operators.

Examples:
- Search all files: `grep(pattern="TODO")`
- Search Python files only: `grep(pattern="import", glob="*.py")`
- Show matching lines: `grep(pattern="error", output_mode="content")`
- Search for code with special chars: `grep(pattern="def __init__(self):")`

## Display Name (`display_name`)

Use plain, action-oriented language. Never mention search patterns or technical terms.
Examples: "Looking up", "Searching for references", "Finding related content"
"""