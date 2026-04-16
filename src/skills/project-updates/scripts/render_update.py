#!/usr/bin/env python3
"""Render a simple project update from JSON input."""

from __future__ import annotations

import json
import sys


def render(payload: dict[str, list[str]]) -> str:
    sections = []
    for heading in ("Progress", "Blockers", "Next Actions"):
        items = payload.get(heading.lower().replace(" ", "_"), [])
        if not items:
            continue
        section = [f"## {heading}"]
        section.extend(f"- {item}" for item in items)
        sections.append("\n".join(section))
    return "\n\n".join(sections)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: render_update.py '<json-payload>'")
    print(render(json.loads(sys.argv[1])))
