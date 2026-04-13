EXECUTE_SCRIPT_TOOL_DESCRIPTION = """Execute a Python script from the skills directory.

Runs a script as a subprocess. Scripts must return a JSON response to stdout with this format:
{
  "status": "success" | "error",
  "message": "Human-readable summary of what was generated",
  "type": "geojson" | "json" | "md" | "csv" | "txt",
  "data": <the actual data payload>
}

On success, the data is automatically saved to VFS. The save location depends on the output type:
- geojson: saved at root — /<script_name>.geojson
- All other types: saved in data/ — /data/<script_name>.<type>

You can override the save location with the `destination_path` parameter.

Parameters:
- script_path: Path to the script relative to the skills directory (e.g. "payroll/scripts/compute_payroll.py")
- script_args: Optional list of command-line arguments to pass to the script
- payload_json: Optional JSON string to pass via --payload-json argument
- destination_path: Optional VFS path to save the output. If omitted, the path is auto-derived from the script name and output type.

Default save locations:
  execute_script(script_path="tax-compliance/scripts/compute_vat.py", ...)
    -> /data/compute_vat.json  (json in data/)

  execute_script(script_path="payroll/scripts/compute_payroll.py", ...)
    -> /data/compute_payroll.json  (json in data/)

  execute_script(script_path="payroll/scripts/compute_payroll.py", ..., destination_path="/data/march_payroll.json")
    -> /data/march_payroll.json  (custom path)
"""
