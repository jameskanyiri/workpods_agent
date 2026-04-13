from .schema import Todo, VFile


def replace_todos_list(left: list[Todo] | None, right: list[Todo] | None) -> list[Todo]:
    """
    Custom reducer for todos list.

    - If right is provided and is a list, it replaces left
    """
    if right is None:
        return left or []
    return right if isinstance(right, list) else (left or [])


def merge_vfs(left: dict[str, VFile], right: dict[str, VFile]) -> dict[str, VFile]:
    """
    Custom reducer for the virtual filesystem.

    Merges right into left. A VFile with empty content signals deletion.
    """
    merged = dict(left or {})
    if right:
        for path, vfile in right.items():
            if vfile.get("content") is None:
                merged.pop(path, None)
            else:
                merged[path] = vfile
    return merged
