#!/usr/bin/env python3
"""Validate minimum project-create fields before the agent writes."""

from __future__ import annotations

import json
import sys


REQUIRED_FIELDS = ("name",)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_project_create.py '<json-payload>'")
    payload = json.loads(sys.argv[1])
    missing = [field for field in REQUIRED_FIELDS if not payload.get(field)]
    if missing:
        raise SystemExit(f"missing required fields: {', '.join(missing)}")
    print("ok")


if __name__ == "__main__":
    main()
