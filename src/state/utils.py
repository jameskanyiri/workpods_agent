from .schema import VFile


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
