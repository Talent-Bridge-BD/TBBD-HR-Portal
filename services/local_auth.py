import os
from typing import Optional

from fastapi import Request


LOCAL_CANDIDATE_ID = "0a516aec-41c2-46d8-9e31-0a4af12b4eda"
LOCAL_CANDIDATE_EMAIL = "tarequeahmed@example.com"
LOCAL_CANDIDATE_NAME = "Tareque Ahmed"
CANDIDATE_GROUP_ID = "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6"


def is_local_auth_enabled() -> bool:
    return (
        os.getenv("TBBD_ENV") == "development"
        and os.getenv("TBBD_LOCAL_AUTH") == "1"
    )


def get_local_principal() -> dict:
    return {
        "id": LOCAL_CANDIDATE_ID,
        "name": LOCAL_CANDIDATE_NAME,
        "email": LOCAL_CANDIDATE_EMAIL,
        "claims": [
            {
                "typ": "name",
                "val": LOCAL_CANDIDATE_NAME,
            },
            {
                "typ": "groups",
                "val": CANDIDATE_GROUP_ID,
            },
            {
                "typ": "roles",
                "val": "Candidate",
            },
        ],
    }


def get_request_principal(request: Request) -> Optional[dict]:
    """
    Production:
      Read the Microsoft Entra / Easy Auth principal from request headers.

    Local development:
      If TBBD_ENV=development and TBBD_LOCAL_AUTH=1, use the fixed
      local Candidate test identity.
    """
    if is_local_auth_enabled():
        return get_local_principal()

    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    encoded_principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not principal_id or not encoded_principal:
        return None

    import base64
    import json

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
