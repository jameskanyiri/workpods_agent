"""
generate_diagram.py
-------------------
Standalone utility to generate data-driven charts as PNG files via QuickChart.io.

No API keys required. No LLM dependencies.

Usage:
    python generate_diagram.py --type bar_chart --data "Month: Jan,Feb,Mar | Values: 120,145,98" --title "Monthly Output"
    python generate_diagram.py --type bar_chart --data "Month: Jan,Feb,Mar | Values: 120,145,98" --output my_chart.png

Requirements:
    pip install requests
"""

from __future__ import annotations

import argparse
import base64
import sys
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Chart type detection
# ---------------------------------------------------------------------------

CHART_TYPES = {
    "bar_chart", "line_chart", "pie_chart", "doughnut_chart",
    "scatter_chart", "area_chart", "horizontal_bar_chart",
    "stacked_bar_chart", "grouped_bar_chart", "radar_chart",
}

CHART_TYPE_MAP = {
    "bar_chart": "bar",
    "horizontal_bar_chart": "horizontalBar",
    "line_chart": "line",
    "pie_chart": "pie",
    "doughnut_chart": "doughnut",
    "area_chart": "line",
    "radar_chart": "radar",
    "stacked_bar_chart": "bar",
    "grouped_bar_chart": "bar",
    "scatter_chart": "scatter",
}

# Color palette for multiple datasets
COLORS = [
    "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
    "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b",
]


def is_chart_type(diagram_type: str) -> bool:
    return diagram_type.lower() in CHART_TYPES


# ---------------------------------------------------------------------------
# Chart.js config builders
# ---------------------------------------------------------------------------

def _build_chartjs_config(diagram_type: str, data: str, title: str) -> dict | None:
    """
    Parse data into a Chart.js config. Supports multiple input formats:

    1. Pipe-delimited (simple):
        "Categories: Jan,Feb,Mar | Values: 120,145,98"
        "Categories: Jan,Feb,Mar | Series A: 10,20,30 | Series B: 40,50,60"

    2. JSON array of objects (rich):
        '[{"label":"Project IRR","project":64.19,"benchmark":15}, ...]'

    3. JSON object with labels + datasets:
        '{"labels":["Jan","Feb"],"datasets":[{"label":"GHI","data":[180,190]}]}'
    """
    ct = CHART_TYPE_MAP.get(diagram_type.lower(), "bar")

    # Try JSON parsing first
    config = _try_json_data(ct, data, title, diagram_type)
    if config:
        return config

    # Fall back to pipe-delimited parsing
    config = _try_pipe_data(ct, data, title, diagram_type)
    if config:
        return config

    return None


def _try_json_data(ct: str, data: str, title: str, diagram_type: str) -> dict | None:
    """Try to parse data as JSON and build Chart.js config."""
    try:
        parsed = json.loads(data)
    except (json.JSONDecodeError, ValueError):
        return None

    try:
        # Format 3: Full Chart.js-like structure {"labels": [...], "datasets": [...]}
        if isinstance(parsed, dict) and "labels" in parsed and "datasets" in parsed:
            datasets = []
            for i, ds in enumerate(parsed["datasets"]):
                datasets.append({
                    "label": ds.get("label", f"Series {i+1}"),
                    "data": ds["data"],
                    "backgroundColor": COLORS[i % len(COLORS)],
                    "borderColor": COLORS[i % len(COLORS)],
                    "fill": diagram_type == "area_chart",
                })
            return _wrap_config(ct, parsed["labels"], datasets, title, diagram_type)

        # Format 2: Array of objects [{"label": "A", "value1": 10, "value2": 20}, ...]
        if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
            first = parsed[0]
            label_key = None
            value_keys = []
            for k, v in first.items():
                if label_key is None and isinstance(v, str):
                    label_key = k
                elif isinstance(v, (int, float)):
                    value_keys.append(k)

            if not label_key or not value_keys:
                return None

            labels = [item.get(label_key, "") for item in parsed]
            datasets = []
            for i, vk in enumerate(value_keys):
                datasets.append({
                    "label": vk.replace("_", " ").title(),
                    "data": [item.get(vk, 0) for item in parsed],
                    "backgroundColor": COLORS[i % len(COLORS)],
                    "borderColor": COLORS[i % len(COLORS)],
                    "fill": diagram_type == "area_chart",
                })
            return _wrap_config(ct, labels, datasets, title, diagram_type)

    except Exception:
        return None

    return None


def _try_pipe_data(ct: str, data: str, title: str, diagram_type: str) -> dict | None:
    """Try to parse pipe-delimited data and build Chart.js config."""
    try:
        parts = [p.strip() for p in data.split("|")]
        if len(parts) < 2:
            return None

        labels_part = parts[0]
        if ":" not in labels_part:
            return None

        _, label_vals = labels_part.split(":", 1)
        labels = [v.strip() for v in label_vals.split(",")]

        datasets = []
        for i, part in enumerate(parts[1:]):
            if ":" not in part:
                return None
            series_name, value_str = part.split(":", 1)
            values = []
            for v in value_str.split(","):
                v = v.strip()
                try:
                    values.append(float(v))
                except ValueError:
                    return None
            datasets.append({
                "label": series_name.strip(),
                "data": values,
                "backgroundColor": COLORS[i % len(COLORS)],
                "borderColor": COLORS[i % len(COLORS)],
                "fill": diagram_type == "area_chart",
            })

        return _wrap_config(ct, labels, datasets, title, diagram_type)

    except Exception:
        return None


def _wrap_config(ct: str, labels: list, datasets: list, title: str, diagram_type: str) -> dict:
    """Wrap labels and datasets into a complete Chart.js config."""
    config = {
        "type": ct,
        "data": {
            "labels": labels,
            "datasets": datasets,
        },
        "options": {
            "plugins": {
                "title": {
                    "display": bool(title),
                    "text": title,
                }
            },
            "scales": (
                {"y": {"beginAtZero": True}}
                if ct not in ("pie", "doughnut", "radar", "scatter")
                else {}
            ),
        },
    }

    # Stacked bar chart config
    if diagram_type == "stacked_bar_chart":
        config["options"]["scales"] = {
            "x": {"stacked": True},
            "y": {"stacked": True, "beginAtZero": True},
        }

    return config


# ---------------------------------------------------------------------------
# QuickChart.io renderer
# ---------------------------------------------------------------------------

def _generate_chart_quickchart(diagram_type: str, data: str, title: str) -> str:
    """Generate a chart via QuickChart.io and return base64 PNG."""
    try:
        import requests
    except ImportError:
        print("[quickchart] 'requests' not installed. Run: pip install requests", file=sys.stderr)
        return ""

    config = _build_chartjs_config(diagram_type, data, title)
    if not config:
        print("[quickchart] Could not parse data into Chart.js config", file=sys.stderr)
        return ""

    try:
        payload = {
            "chart": json.dumps(config),
            "width": 900,
            "height": 550,
            "backgroundColor": "white",
            "format": "png",
        }
        response = requests.post(
            "https://quickchart.io/chart",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    except Exception as e:
        print(f"[quickchart] Request failed: {e}", file=sys.stderr)
        return ""


# ---------------------------------------------------------------------------
# Public utility function
# ---------------------------------------------------------------------------

def generate_diagram_base64(
    diagram_type: str,
    data: str,
    title: str = "",
) -> str:
    """
    Generate a data-driven chart and return it as a raw base64-encoded PNG string.

    Uses QuickChart.io (Chart.js) — no API keys or LLM dependencies.

    Args:
        diagram_type:  One of the CHART_TYPES (e.g. "bar_chart", "line_chart",
                       "pie_chart", "doughnut_chart", "scatter_chart", "area_chart",
                       "horizontal_bar_chart", "stacked_bar_chart", "grouped_bar_chart",
                       "radar_chart").
        data:          Data string. Accepted formats:
                       - Pipe-delimited: "Categories: Jan,Feb,Mar | Values: 120,145,98"
                       - JSON array: '[{"label":"A","val":10}, ...]'
                       - JSON object: '{"labels":[...],"datasets":[...]}'
        title:         Optional chart title.

    Returns:
        Raw base64 string (no data URI prefix), or empty string on failure.
    """
    print(f"\nGenerating chart — type='{diagram_type}', title='{title}'", file=sys.stderr)

    if not is_chart_type(diagram_type):
        print(f"[error] Unsupported chart type: '{diagram_type}'. "
              f"Supported types: {', '.join(sorted(CHART_TYPES))}", file=sys.stderr)
        return ""

    b64 = _generate_chart_quickchart(diagram_type, data, title)
    if b64:
        print("[chart] Generated successfully via QuickChart.io", file=sys.stderr)
    return b64


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save_diagram(b64: str, output_path: str) -> None:
    """Decode base64 and write PNG bytes to disk."""
    image_bytes = base64.b64decode(b64)
    Path(output_path).write_bytes(image_bytes)
    print(f"\nSaved diagram to: {output_path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _run_from_payload(payload: dict) -> None:
    """Run diagram generation from a structured payload dict (used by execute_script).

    Payload format:
        {
            "type": "bar_chart",
            "data": "Month: Jan,Feb,Mar | Values: 120,145,98",
            "title": "Monthly Output",
            "output_name": "monthly_output",
            "name": "monthly_output",
            "description": "Monthly energy output chart"
        }

    Outputs standardised JSON to stdout for VFS integration.
    The ``data`` object uses the same schema as API-extracted plot files:
        {
            "status": "success",
            "message": "Diagram generated: monthly_output",
            "type": "png_base64",
            "data": {
                "file_id": "monthly_output",
                "name": "monthly_output",
                "title": "Monthly Output",
                "description": "Monthly energy output chart",
                "mime_type": "image/png",
                "image_base64": "<BASE64_IMAGE_DATA>"
            }
        }
    """
    diagram_type = payload.get("type", "")
    data = payload.get("data", "")
    title = payload.get("title", "")
    output_name = payload.get("output_name", "diagram")
    name = payload.get("name", output_name)
    description = payload.get("description", "")

    if not diagram_type or not data:
        result = {
            "status": "error",
            "message": "Payload must include 'type' and 'data' fields.",
            "type": "json",
            "data": None,
        }
        print(json.dumps(result))
        sys.exit(1)

    b64 = generate_diagram_base64(
        diagram_type=diagram_type,
        data=data,
        title=title,
    )

    if not b64:
        result = {
            "status": "error",
            "message": f"Chart generation failed for type '{diagram_type}'. "
                       f"Supported types: {', '.join(sorted(CHART_TYPES))}",
            "type": "json",
            "data": None,
        }
        print(json.dumps(result))
        sys.exit(1)

    file_id = output_name
    result = {
        "status": "success",
        "message": f"Diagram generated: {file_id}",
        "type": "png_base64",
        "data": {
            "file_id": file_id,
            "name": name,
            "title": title,
            "description": description,
            "mime_type": "image/png",
            "image_base64": b64,
        },
    }
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(
        description="Generate data-driven charts as PNG files via QuickChart.io.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bar chart from pipe-delimited data
  python generate_diagrams.py --type bar_chart \\
      --data "Month: Jan,Feb,Mar,Apr | Values: 120,145,98,160" \\
      --title "Monthly Energy Output (MWh)"

  # Pie chart
  python generate_diagrams.py --type pie_chart \\
      --data "Source: Solar,Wind,Gas,Hydro | Values: 40,30,20,10" \\
      --title "Generation Mix" \\
      --output generation_mix.png

  # VFS mode (used by execute_script with --payload-json)
  python generate_diagrams.py --payload-json '{
      "type": "bar_chart",
      "data": "Month: Jan,Feb,Mar | Values: 120,145,98",
      "title": "Monthly Output",
      "output_name": "monthly_output"
  }'

Supported chart types:
  bar_chart, line_chart, pie_chart, doughnut_chart, scatter_chart,
  area_chart, horizontal_bar_chart, stacked_bar_chart, grouped_bar_chart,
  radar_chart

Data formats:
  Pipe-delimited:  "Labels: A,B,C | Values: 10,20,30"
  Multi-series:    "Labels: A,B,C | Series1: 10,20,30 | Series2: 5,8,12"
  JSON array:      '[{"label":"A","val1":10,"val2":5}, ...]'
  JSON object:     '{"labels":["A","B"],"datasets":[{"label":"S1","data":[10,20]}]}'
        """,
    )
    parser.add_argument("--type", default="", help="Chart type (e.g. bar_chart, pie_chart)")
    parser.add_argument("--data", default="", help="Data string (pipe-delimited or JSON)")
    parser.add_argument("--title", default="", help="Optional chart title")
    parser.add_argument("--name", default="", help="Human-readable name for the diagram")
    parser.add_argument("--description", default="", help="Description of what the diagram shows")
    parser.add_argument("--output", default="diagram.png", help="Output PNG file path (default: diagram.png)")
    parser.add_argument("--payload-json", default="", help="JSON payload for VFS integration mode")

    args = parser.parse_args()

    # VFS integration mode: structured JSON in, structured JSON out
    if args.payload_json:
        payload = json.loads(args.payload_json)
        _run_from_payload(payload)
        return

    # CLI mode: direct args — also outputs standard JSON to stdout
    # so execute_script can always parse the result and save to VFS.
    if not args.type or not args.data:
        parser.error("--type and --data are required (or use --payload-json)")

    # Derive output_name from --output flag (strip path and extension)
    output_name = Path(args.output).stem

    # Reuse the payload path so output is always standard JSON
    _run_from_payload({
        "type": args.type,
        "data": args.data,
        "title": args.title,
        "name": args.name or output_name,
        "description": args.description,
        "output_name": output_name,
    })


if __name__ == "__main__":
    main()
