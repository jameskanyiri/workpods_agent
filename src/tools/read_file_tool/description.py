READ_FILE_TOOL_DESCRIPTION = """Reads a file from the filesystem.

Assume this tool is able to read all files. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

Usage:
- By default, it reads up to 100 lines starting from the beginning of the file
- **IMPORTANT for large files and codebase exploration**: Use pagination with offset and limit parameters to avoid context overflow
  - First scan: read_file(path, limit=100) to see file structure
  - Continue: read_file(path, offset=100, limit=200) for next 200 lines
  - Only omit limit (read full file) when necessary for editing
- Specify offset and limit: read_file(path, offset=0, limit=100) reads first 100 lines
- Results are returned using cat -n format, with line numbers starting at 1
- You should ALWAYS make sure a file has been read before editing it.

You have access to two file systems:
1. **local** — for anything related to skills (references, templates, scripts, examples)
2. **vfs** — for workspace content (generated documents, project data, script outputs)

Use the `storage_type` parameter to select:
- storage_type="local" — read from the local skills directory
- storage_type="vfs" (default) — read from the virtual filesystem

Examples:
- read_file(file_path="payroll/references/paye_brackets.md", storage_type="local") — read a skill reference file
- read_file(file_path="tax-compliance/assets/vat_return/master.md", storage_type="local") — read a master template for planning
- read_file(file_path="tax-compliance/assets/vat_return/sections/02_output_vat.md", storage_type="local") — read a section template for writing
- read_file(file_path="/acme-ltd/data/trial_balance.json") — read generated data from VFS

Rule: Skills are always in local. Everything else is in VFS."""
