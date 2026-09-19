import base64
import json
from typing import Optional

from fastapi import Request


def get_request_principal(request: Request) -> Optional[dict]:
    """
    Read the Microsoft Entra / Easy Auth principal from request headers.
    """
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    encoded_principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not principal_id or not encoded_principal:
        return None

    try:
        padding = "=" * (-len(encoded_principal) % 4)
        principal = json.loads(
            base64.b64decode(
                encoded_principal + padding
            ).decode("utf-8")
        )
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    principal["id"] = principal_id
    principal["email"] = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL-NAME"
    )

    return principal
