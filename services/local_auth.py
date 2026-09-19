import base64
import json
from typing import Optional

import jwt
import requests
from fastapi import Request


TBBD_TENANT_ID = "319c9d59-c5f1-48d3-af49-4f959b5e02c1"
TBBD_CLIENT_ID = "16835108-56db-49f8-a566-a52bc0691cec"

ENTRA_ISSUER = (
    f"https://login.microsoftonline.com/"
    f"{TBBD_TENANT_ID}/v2.0"
)

ENTRA_JWKS_URL = (
    f"https://login.microsoftonline.com/"
    f"{TBBD_TENANT_ID}/discovery/v2.0/keys"
)


def _get_easy_auth_principal(request: Request) -> Optional[dict]:
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


def _get_bearer_token(request: Request) -> Optional[str]:
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        return None

    token = authorization[7:].strip()

    return token or None


def _get_entra_principal(request: Request) -> Optional[dict]:
    token = _get_bearer_token(request)

    if not token:
        return None

    try:
        signing_key = jwt.PyJWKClient(
            ENTRA_JWKS_URL
        ).get_signing_key_from_jwt(token)

        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=TBBD_CLIENT_ID,
            issuer=ENTRA_ISSUER,
        )
    except (
        jwt.PyJWTError,
        requests.RequestException,
        ValueError,
    ):
        return None

    principal_id = claims.get("oid")

    if not principal_id:
        return None

    email = (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or ""
    )

    principal_claims = []

    for group_id in claims.get("groups", []):
        principal_claims.append(
            {
                "typ": "groups",
                "val": group_id,
            }
        )

    for role in claims.get("roles", []):
        principal_claims.append(
            {
                "typ": "roles",
                "val": role,
            }
        )

    principal_claims.extend(
        [
            {
                "typ": "oid",
                "val": principal_id,
            },
            {
                "typ": "tid",
                "val": claims.get("tid", ""),
            },
        ]
    )

    return {
        "id": principal_id,
        "email": email,
        "claims": principal_claims,
    }


def get_request_principal(request: Request) -> Optional[dict]:
    """
    Resolve the authenticated Microsoft Entra principal.

    Production:
        Azure App Service Easy Auth headers.

    Local development:
        Microsoft Entra Bearer access token.
    """

    easy_auth_principal = _get_easy_auth_principal(request)

    if easy_auth_principal:
        return easy_auth_principal

    return _get_entra_principal(request)
