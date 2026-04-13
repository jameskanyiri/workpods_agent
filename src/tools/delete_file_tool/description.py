DELETE_FILE_TOOL_DESCRIPTION = """Delete a file from the virtual filesystem or the local skills directory.

Use this tool when you need to:
- Remove an outdated plan before creating a new one
- Clean up files that are no longer needed
- Replace a file by deleting it first, then writing a new version

IMPORTANT RULES:
- Always read or list files before deleting to confirm the correct path.
- You should only have ONE active plan at a time. Delete the previous plan before creating a new one.
- Do not delete files the user has uploaded unless they explicitly ask you to.

Parameters:
- file_path (str, required): Path of the file to delete.
- storage_type (str, optional): "vfs" (default) for virtual filesystem, "local" for the skills directory.
- display_name (str, optional): Short label for the frontend. Default: "Deleting file".
"""
