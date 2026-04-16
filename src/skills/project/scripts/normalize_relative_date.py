#!/usr/bin/env python3
"""Normalize simple relative date phrases into YYYY-MM-DD."""

from __future__ import annotations

import re
import sys
from datetime import date


def add_years_safe(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + years)


def normalize(text: str, today: date) -> str:
    value = text.strip().lower()
    if value == "today":
        return today.isoformat()
    if value == "tomorrow":
        return today.fromordinal(today.toordinal() + 1).isoformat()
    match = re.fullmatch(r"(\d+)\s+(day|days|week|weeks|month|months|year|years)\s+from\s+today", value)
    if not match:
        raise ValueError(f"Unsupported relative date phrase: {text}")
    amount = int(match.group(1))
    unit = match.group(2)
    if unit.startswith("day"):
        return today.fromordinal(today.toordinal() + amount).isoformat()
    if unit.startswith("week"):
        return today.fromordinal(today.toordinal() + (amount * 7)).isoformat()
    if unit.startswith("month"):
        month_index = (today.month - 1) + amount
        year = today.year + (month_index // 12)
        month = (month_index % 12) + 1
        day = min(today.day, 28)
        return date(year, month, day).isoformat()
    return add_years_safe(today, amount).isoformat()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: normalize_relative_date.py '<phrase>'")
    print(normalize(sys.argv[1], date.today()))
