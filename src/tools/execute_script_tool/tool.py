import json
import os
import subprocess
import sys
import uuid
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from .description import EXECUTE_SCRIPT_TOOL_DESCRIPTION

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "skills")

# Map script result "type" to file extensions
TYPE_TO_EXT = {
    "geojson": ".geojson",
    "json": ".json",
    "md": ".md",
    "csv": ".csv",
    "txt": ".txt",
}

DEFAULT_SCRIPT_TIMEOUT_SECONDS = 360
LONG_RUNNING_SCRIPT_TIMEOUT_SECONDS = 1200
LONG_RUNNING_SCRIPT_PATHS = {
    "payroll/scripts/compute_payroll.py",
    "bank-reconciliation/scripts/match_transactions.py",
}


def _build_vfs_path(script_path: str, file_type: str) -> str:
    """Derive a VFS file path from the script path and result type.

    - geojson files are saved at the root: /<script_name>.geojson
    - All other types are saved in data/: /data/<script_name>.<ext>

    Examples:
        tax-compliance/scripts/compute_vat.py + json
            -> /data/compute_vat.json

        payroll/scripts/compute_payroll.py + csv
            -> /data/compute_payroll.csv
    """
    script_name = os.path.splitext(os.path.basename(script_path))[0]
    ext = TYPE_TO_EXT.get(file_type, f".{file_type}")

    if file_type == "geojson":
        return f"/{script_name}{ext}"

    return f"/data/{script_name}{ext}"


def _serialize_data(data: object, file_type: str) -> str:
    """Serialize the data field to a string suitable for VFS storage."""
    if isinstance(data, str):
        return data
    if file_type in ("json", "geojson"):
        return json.dumps(data, indent=2, ensure_ascii=False)
    return str(data)


def _build_diagram_record(file_data: dict) -> tuple[str, str]:
    """Build a consistent diagram JSON record for VFS storage.

    All diagram files (generated charts and API-extracted plots) share
    the same schema: file_id, name, title, description, mime_type, image_base64.

    Returns (json_string, file_id).
    """
    file_id = file_data.get("file_id", f"diagram-{uuid.uuid4().hex[:12]}")
    record = json.dumps({
        "file_id": file_id,
        "name": file_data.get("name", file_id),
        "title": file_data.get("title", ""),
        "description": file_data.get("description", ""),
        "mime_type": file_data.get("mime_type", "image/png"),
        "image_base64": file_data.get("image_base64", ""),
    }, indent=2)
    return record, file_id


def _script_timeout_seconds(script_path: str) -> int:
    normalized_script_path = script_path.replace("\\", "/")
    if normalized_script_path in LONG_RUNNING_SCRIPT_PATHS:
        return LONG_RUNNING_SCRIPT_TIMEOUT_SECONDS
    return DEFAULT_SCRIPT_TIMEOUT_SECONDS


def _parse_script_stdout(stdout: str) -> dict | None:
    stdout = stdout.strip()
    if not stdout:
        return None
    try:
        return json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return None


def _format_script_error_message(
    *,
    message: str,
    data: object = None,
    stderr: str = "",
    returncode: int | None = None,
) -> str:
    parts = [f"Script error: {message or 'Unknown script error.'}"]

    if isinstance(data, dict):
        status_code = data.get("status_code")
        detail = data.get("detail")
        recovery_hint = data.get("recovery_hint")
        expected_contract = data.get("expected_contract")

        if status_code is not None:
            parts.append(f"HTTP status: {status_code}")
        if detail is not None:
            if isinstance(detail, str):
                parts.append(f"Detail: {detail}")
            else:
                parts.append(f"Detail: {json.dumps(detail, ensure_ascii=False)}")
        if recovery_hint:
            parts.append(f"Recovery: {recovery_hint}")
        if expected_contract:
            parts.append(f"Expected contract: {json.dumps(expected_contract, ensure_ascii=False)}")

    if stderr:
        parts.append(stderr.rstrip())
    if returncode is not None:
        parts.append(f"[exit code: {returncode}]")
    return "\n".join(parts)


@tool(description=EXECUTE_SCRIPT_TOOL_DESCRIPTION)
def execute_script(
    display_name: str = "Executing script",
    script_path: str = "",
    script_args: list[str] = [],
    payload_json: str = "",
    destination_path: str = "",
    runtime: ToolRuntime = None,
) -> Command:
    """Execute a Python script from the skills directory."""

    full_path = os.path.normpath(os.path.join(SKILLS_DIR, script_path))

    # Ensure the resolved path is within the skills directory
    if not full_path.startswith(os.path.normpath(SKILLS_DIR)):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: script_path must be within the skills directory. Got: {script_path}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    if not os.path.isfile(full_path):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: script not found at '{script_path}'. Ensure the path is relative to the skills directory.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    cmd = [sys.executable, full_path]

    if payload_json:
        cmd.extend(["--payload-json", payload_json])

    if script_args:
        cmd.extend(script_args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_script_timeout_seconds(script_path),
            cwd=os.path.dirname(full_path),
        )
        stdout = result.stdout.strip()
        script_result = _parse_script_stdout(stdout)

        if result.returncode != 0:
            if isinstance(script_result, dict):
                message = script_result.get("message", "")
                data = script_result.get("data")
                content = _format_script_error_message(
                    message=message,
                    data=data,
                    stderr=result.stderr,
                    returncode=result.returncode,
                )
            else:
                error_parts = []
                if result.stderr:
                    error_parts.append(result.stderr)
                if stdout:
                    error_parts.append(stdout)
                error_parts.append(f"[exit code: {result.returncode}]")
                content = "\n".join(error_parts)
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=content,
                            tool_call_id=runtime.tool_call_id,
                        )
                    ]
                }
            )

        # Parse the standardised script response
        if script_result is None:
            # Script didn't return valid JSON — return raw output
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=stdout or "(no output)",
                            tool_call_id=runtime.tool_call_id,
                        )
                    ]
                }
            )

        status = script_result.get("status", "error")
        message = script_result.get("message", "")
        file_type = script_result.get("type", "json")
        data = script_result.get("data")

        if status == "error":
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=_format_script_error_message(message=message, data=data),
                            tool_call_id=runtime.tool_call_id,
                        )
                    ]
                }
            )

        # Build VFS update
        state_update: dict = {}
        vfs_entries: dict = {}

        if data is not None:
            if file_type == "png_base64":
                # Diagram from generate_diagrams.py — data already has the
                # consistent schema (file_id, name, title, description,
                # mime_type, image_base64).
                file_data = data if isinstance(data, dict) else {"image_base64": str(data)}
                diagram_record, file_id = _build_diagram_record(file_data)
                title = file_data.get("title", "")
                vfs_path = destination_path if destination_path else f"/diagrams/{file_id}.json"

                vfs_entries[vfs_path] = {"path": vfs_path, "content": diagram_record}
                message = (
                    f"{message}\n\n"
                    f"Diagram ID: `{file_id}`\n"
                    f"VFS path: {vfs_path}\n\n"
                    f"Embed in your document using:\n"
                    f'<img src="{{{{{file_id}}}}}" alt="{title}" width="900" />'
                )
            else:
                # Check if the response contains extracted files (has_files pattern)
                # API responses may return {has_files, data: {result, files}}
                api_response = data
                extracted_files = []

                if isinstance(api_response, dict) and api_response.get("has_files") and "data" in api_response:
                    inner_data = api_response["data"]
                    extracted_files = inner_data.get("files", [])
                    data_to_store = inner_data.get("result", inner_data)
                else:
                    data_to_store = data

                # Save the structured data to VFS
                vfs_path = destination_path if destination_path else _build_vfs_path(script_path, file_type)
                file_content = _serialize_data(data_to_store, file_type)
                vfs_entries[vfs_path] = {"path": vfs_path, "content": file_content}
                message = f"{message}\n\nFile saved to: {vfs_path}"

                # Save each extracted file — same schema via _build_diagram_record
                if extracted_files:
                    file_ids = []
                    for plot_file in extracted_files:
                        diagram_record, file_id = _build_diagram_record(plot_file)
                        diagram_path = f"/diagrams/{file_id}.json"
                        vfs_entries[diagram_path] = {"path": diagram_path, "content": diagram_record}
                        file_ids.append(file_id)

                    message += (
                        f"\n\n{len(extracted_files)} plot files extracted and saved to /diagrams/."
                        f"\n\nEmbed in documents using:"
                        f'\n<img src="{{{{<file_id>}}}}" alt="title" width="900" />'
                        f"\n\nAvailable file IDs:\n"
                        + "\n".join(f"- `{fid}`" for fid in file_ids)
                    )

        if vfs_entries:
            state_update["vfs"] = vfs_entries

        state_update["messages"] = [
            ToolMessage(
                content=message,
                tool_call_id=runtime.tool_call_id,
            )
        ]

        return Command(update=state_update)

    except subprocess.TimeoutExpired:
        content = "Error: script execution timed out after 360 seconds."
    except Exception as e:
        content = f"Error executing script: {e}"

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=content,
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )
