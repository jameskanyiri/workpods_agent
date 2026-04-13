# Tools Reference

Documentation for all tools available in the orchestrator agent.

---

## 1. ask_user_input

**Description:** Ask the user structured questions with predefined answer options. Use this instead of open-ended text questions when you need the user to choose between clear options, select preferences, or rank priorities.

**When to use:**
- You need the user to pick a direction (e.g. which document to draft first)
- You need preferences or priorities (e.g. which sections matter most)
- You need a yes/no or A/B/C decision
- You want to confirm understanding before acting

**When NOT to use:**
- You need free-form input (names, descriptions, details) — just ask in a normal message
- The answer requires explanation or nuance that can't fit in 2-4 short options

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `questions` | `list[Question]` | Yes | — | 1 to 3 question objects (see schema below) |
| `display_name` | `str` | No | `"Waiting for your input"` | Short label for the frontend. Never use file names or extensions. |

#### Question Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | `str` | Yes | — | The question text shown to the user. Use plain, non-technical language. |
| `type` | `"single_select" \| "multi_select" \| "rank_priorities"` | No | `"single_select"` | How the user answers: `single_select` = pick one, `multi_select` = pick one or more, `rank_priorities` = drag to reorder. |
| `options` | `list[str]` | Yes | — | 2 to 4 answer choices. Keep labels short and clear. |

### Constraints
- Max 3 questions per call
- 2 to 4 options per question
- Keep option labels short (2-5 words)
- Use plain, non-technical language — never use file names, paths, or tool names

---

## 2. think_tool

**Description:** Pause and reflect on what has been done and plan what to do next. Used for internal reasoning — first person, confident, clear.

**When to use:**
- After receiving task results, before deciding next steps
- When you need to reason about findings before acting

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `reflection` | `str` | Yes | — | 2-3 sentences in first person — what was found/confirmed, what to do next and why. Max 50 words. No file names or technical terms. |

### Rules
- Always use "I" — contractions preferred ("I'm", "I've", "I'll")
- Be specific about content (name the section, field, problem) but never mention file names, paths, or tool names
- Max 3 sentences, 50 words

---

## 3. write_todos

**Description:** Creates and manages a structured task list for the current session. Replaces the entire todo list on every call — always pass the full list when updating.

**When to use:**
- Plan tasks after a complex request (typically right after `think_tool`)
- Mark a task as `in_progress` when you start it, `completed` when you finish
- Update the description as you work

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `todos` | `list[TodoItem]` | Yes | — | Full list of todo items (replaces existing list) |
| `display_name` | `str` | No | `"Updating tasks"` | Reflects the action in plain language. Never use file names or extensions. |

#### TodoItem Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | `str` | Yes | — | Unique identifier (e.g. `"1"`, `"2"`) |
| `label` | `str` | Yes | — | Short display title, 5-8 words max (e.g. `"Draft executive summary"`) |
| `status` | `"pending" \| "in_progress" \| "completed"` | Yes | — | Task status |
| `description` | `str` | Yes | — | Detailed breakdown of what this task involves, inputs needed, expected output. For completed tasks: what was done, decisions made, files created. |

### Rules
- Only one task should be `in_progress` at a time
- Always pass the full list — partial updates overwrite existing tasks
- Never leave `description` empty

---

## 4. write_file

**Description:** Writes content to a new file in the virtual filesystem. Prefer editing existing files over creating new ones when possible.

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `str` | Yes | — | Path for the new file |
| `content` | `str` | Yes | — | Content to write to the file |
| `display_name` | `str` | No | `"Creating file"` | Short label for the frontend |

### Behavior
- Returns an error if the file already exists (use `edit_file` instead)
- Returns confirmation with character count on success

---

## 5. edit_file

**Description:** Performs exact string replacements in existing files. You must read the file before editing.

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `str` | Yes | — | Path to the file to edit |
| `old_string` | `str` | Yes | — | The exact text to find and replace |
| `new_string` | `str` | Yes | — | The replacement text |
| `display_name` | `str` | No | `"Editing file"` | Short label for the frontend |

### Behavior
- Errors if the file is not found
- Errors if `old_string` is not found in the file
- Errors if `old_string` matches more than once — provide more context to make it unique
- Replaces only the first (unique) occurrence

---

## 6. read_file

**Description:** Reads a file from the virtual filesystem with pagination support.

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `str` | Yes | — | Path to the file to read |
| `offset` | `int` | No | `0` | Line number to start reading from (0-indexed) |
| `limit` | `int` | No | `100` | Number of lines to read |
| `display_name` | `str` | No | `"Reading file"` | Short label for the frontend |

### Behavior
- Returns lines in `cat -n` format with line numbers starting at 1
- Returns a header showing file path and line range
- Returns an error if the file is not found
- Supports image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`) as multimodal content — do not use `offset`/`limit` for images

### Pagination Tips
- First scan: `read_file(path, limit=100)` to see file structure
- Read more: `read_file(path, offset=100, limit=200)` for next 200 lines
- Lines longer than 5,000 characters are split with continuation markers (e.g., `5.1`, `5.2`)

---

## 7. glob_tool

**Description:** Find files matching a glob pattern in the virtual filesystem.

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pattern` | `str` | Yes | — | Glob pattern to match. Supports `*` (any characters), `**` (any directories), `?` (single character). |
| `display_name` | `str` | No | `"Searching files"` | Short label for the frontend |

### Examples
- `**/*.py` — Find all Python files
- `*.txt` — Find all text files in root
- `/subdir/**/*.md` — Find all markdown files under `/subdir`

---

## 8. grep_tool

**Description:** Search for a text pattern across files in the virtual filesystem. Uses literal text matching (not regex).

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pattern` | `str` | Yes | — | Text to search for (literal, not regex) |
| `glob` | `str` | No | `""` | Glob pattern to filter which files to search |
| `output_mode` | `str` | No | `"files_with_matches"` | Output format: `"files_with_matches"` (file paths only), `"content"` (matching lines with line numbers), `"count"` (match counts per file) |
| `display_name` | `str` | No | `"Searching content"` | Short label for the frontend |

### Examples
- Search all files: `grep(pattern="TODO")`
- Search Python files only: `grep(pattern="import", glob="*.py")`
- Show matching lines: `grep(pattern="error", output_mode="content")`
- Search for code with special chars: `grep(pattern="def __init__(self):")`

---

## 9. ls_tool

**Description:** Lists all files and directories at a given path. Useful for exploring the filesystem before reading or editing files.

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | `str` | Yes | — | Directory path to list |
| `display_name` | `str` | No | `"Listing files"` | Short label for the frontend |

### Behavior
- Directories are shown with a trailing `/`
- Directories are listed before files
- Only shows the immediate contents (one level deep)

---

## 10. delete_file

**Description:** Delete a file from the virtual filesystem or the local skills directory. Use this to clean up outdated files — for example, removing an old plan before creating a new one.

**When to use:**
- You need to remove an outdated plan before creating a replacement
- You need to clean up files that are no longer needed
- You want to replace a file (delete first, then write the new version)

**When NOT to use:**
- Do not delete files the user uploaded unless they explicitly ask

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `str` | Yes | — | Path of the file to delete |
| `storage_type` | `str` | No | `"vfs"` | `"vfs"` for virtual filesystem, `"local"` for skills directory |
| `display_name` | `str` | No | `"Deleting file"` | Short label for the frontend |

### Behavior
- Returns an error if the file does not exist
- For local files: only allows deletion within the skills directory
- For VFS files: signals deletion via `content: None` in the VFS merge

---

## 11. activate_skill

**Description:** Activate a skill's full instructions and workflow into context. Use this when you need the complete workflow, template, or guidelines for a skill before executing a complex task.

### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skill_name` | `str` | Yes | — | The skill identifier (e.g., `"solar-project"`). Must match one of the registered skill names. |
| `display_name` | `str` | No | `"Activating skill"` | Short label describing the action (e.g., `"Activating solar project workflow"`) |

### Behavior
- Looks up the skill name in the skills registry
- If not found, returns the list of available skills
- Activates and returns the full `SKILL.md` content for the matched skill
- Sets the skill as the active skill in state
