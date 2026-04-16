#!/usr/bin/env python3
"""Render a concise markdown status review from JSON input."""

from __future__ import annotations

import json
import sys


HEADINGS = (
    ("blockers", "Blockers"),
    ("milestone_risk", "Milestone Risk"),
    ("progress", "Progress"),
    ("next_recommendation", "Next Recommendation"),
)


def render(payload: dict[str, list[str] | str]) -> str:
    parts: list[str] = []
    for key, heading in HEADINGS:
        value = payload.get(key)
        if not value:
            continue
        if isinstance(value, list):
            section = [f"## {heading}"]
            section.extend(f"- {item}" for item in value)
            parts.append("\n".join(section))
        else:
            parts.append(f"## {heading}\n- {value}")
    return "\n\n".join(parts)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: render_status_review.py '<json-payload>'")
    print(render(json.loads(sys.argv[1])))
