"""Register a user with the backend onboarding endpoint.

Called via execute_script. Expects --payload-json with:
{
    "user_name": "Dr. Wanjiku Kamau",
    "kra_pin": "A123456789Z",
    "practice_type": "General Practice",
    "email": "dr.wanjiku@ada.finance"
}

Returns ScriptResult JSON to stdout.
"""

import argparse
import json
import os
import re
import sys

import httpx

KRA_PIN_PATTERN = re.compile(r"^[A-Z]\d{9}[A-Z]$")


def validate_payload(payload: dict) -> str | None:
    """Validate required fields. Returns error message or None."""
    required = ["user_name", "kra_pin", "practice_type", "email"]
    missing = [f for f in required if not payload.get(f)]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"

    if not KRA_PIN_PATTERN.match(payload["kra_pin"]):
        return (
            f"Invalid KRA PIN format: '{payload['kra_pin']}'. "
            "Expected: uppercase letter + 9 digits + uppercase letter (e.g. A123456789Z)."
        )

    return None


def register(payload: dict) -> dict:
    """Call the backend onboard endpoint."""
    api_url = os.environ.get("ONBOARD_API_URL", "")
    api_key = os.environ.get("ONBOARD_API_KEY", "")

    if not api_url:
        return {
            "status": "error",
            "message": "ONBOARD_API_URL environment variable is not set.",
            "type": "json",
            "data": {"recovery_hint": "Set the ONBOARD_API_URL environment variable."},
        }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = httpx.post(api_url, json=payload, headers=headers, timeout=30)

    if response.status_code >= 400:
        return {
            "status": "error",
            "message": f"Backend returned HTTP {response.status_code}.",
            "type": "json",
            "data": {
                "status_code": response.status_code,
                "detail": response.text,
                "recovery_hint": "Check the backend logs or retry.",
            },
        }

    return {
        "status": "success",
        "message": "User registered successfully.",
        "type": "json",
        "data": response.json() if response.text else {},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload-json", required=True)
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload_json)
    except json.JSONDecodeError as e:
        result = {
            "status": "error",
            "message": f"Invalid JSON payload: {e}",
            "type": "json",
            "data": {},
        }
        print(json.dumps(result))
        sys.exit(1)

    # Validate
    error = validate_payload(payload)
    if error:
        result = {
            "status": "error",
            "message": error,
            "type": "json",
            "data": {"recovery_hint": "Collect the missing or invalid fields and retry."},
        }
        print(json.dumps(result))
        sys.exit(1)

    # Register
    result = register(payload)
    print(json.dumps(result))
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
