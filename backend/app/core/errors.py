from typing import Any


def error_payload(
    *,
    code: str,
    message: str,
    correlation_id: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "correlation_id": correlation_id,
        }
    }
    if details:
        payload["error"]["details"] = details
    return payload
