import base64
import json
from typing import Any, Optional

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

EMAIL_CLAIM_TYPES = {
    "preferred_username",
    "email",
    "upn",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn",
}


def _get_claim_values(claims: Any, claim_type: str) -> list[str]:
    """Extract unique, non-empty values for a claim type."""
    if not isinstance(claims, list):
        return []

    values = []
    seen = set()

    for claim in claims:
        if not isinstance(claim, dict):
            continue

        if str(claim.get("typ", "")).lower() != claim_type.lower():
            continue

        value = claim.get("val")
        if value is None:
            continue

        value = str(value).strip()
        if value and value not in seen:
            values.append(value)
            seen.add(value)

    return values


def _merge_claim_values(
    existing_values: Any,
    claim_values: list[str],
) -> list[str]:
    """Merge existing values with authenticated claims without duplicates."""
    if isinstance(existing_values, str):
        existing_values = [existing_values]

    if not isinstance(existing_values, (list, tuple, set)):
        existing_values = []

    result = []
    seen = set()

    for value in [*existing_values, *claim_values]:
        if not isinstance(value, str):
            continue

        value = value.strip()
        if value and value not in seen:
            result.append(value)
            seen.add(value)

    return result


def _get_easy_auth_principal(request: Request) -> Optional[dict]:
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    encoded_principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not principal_id or not encoded_principal:
        return None

    try:
        padding = "=" * (-len(encoded_principal) % 4)
        decoded = base64.b64decode(
            encoded_principal + padding,
            validate=True,
        ).decode("utf-8")
        principal = json.loads(decoded)
    except (
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return None

    if not isinstance(principal, dict):
        return None

    principal["id"] = principal_id
    claims = principal.get("claims", [])

    if not isinstance(claims, list):
        claims = []

    principal["claims"] = claims

    # Easy Auth commonly provides roles and groups inside "claims".
    # Normalize them for authorization code that reads top-level fields.
    principal["roles"] = _merge_claim_values(
        principal.get("roles"),
        _get_claim_values(claims, "roles"),
    )
    principal["groups"] = _merge_claim_values(
        principal.get("groups"),
        _get_claim_values(claims, "groups"),
    )

    email_claim = next(
        (
            str(claim.get("val")).strip()
            for claim in claims
            if isinstance(claim, dict)
            and str(claim.get("typ", "")).lower() in EMAIL_CLAIM_TYPES
            and claim.get("val")
            and "@" in str(claim.get("val"))
        ),
        "",
    )

    header_name = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL-NAME", ""
    ).strip()

    principal["email"] = email_claim or (
        header_name if "@" in header_name else ""
    )

    name_claim = next(
        (
            str(claim.get("val")).strip()
            for claim in claims
            if isinstance(claim, dict)
            and str(claim.get("typ", "")).lower() == "name"
            and claim.get("val")
        ),
        "",
    )

    if name_claim:
        principal["name"] = name_claim

    return principal


def _get_bearer_token(request: Request) -> Optional[str]:
    authorization = request.headers.get("Authorization", "")
    scheme, separator, credentials = authorization.partition(" ")

    if not separator or scheme.lower() != "bearer":
        return None

    token = credentials.strip()
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

    if not isinstance(principal_id, str) or not principal_id.strip():
        return None

    raw_groups = claims.get("groups", [])
    raw_roles = claims.get("roles", [])

    groups = (
        [value for value in raw_groups if isinstance(value, str) and value]
        if isinstance(raw_groups, list)
        else []
    )
    roles = (
        [value for value in raw_roles if isinstance(value, str) and value]
        if isinstance(raw_roles, list)
        else []
    )

    email = (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or ""
    )

    if not isinstance(email, str):
        email = ""

    name = claims.get("name")

    principal_claims = [
        {"typ": "groups", "val": group_id}
        for group_id in groups
    ]
    principal_claims.extend(
        {"typ": "roles", "val": role}
        for role in roles
    )
    principal_claims.extend(
        [
            {"typ": "oid", "val": principal_id},
            {"typ": "tid", "val": claims.get("tid", "")},
        ]
    )

    principal = {
        "id": principal_id,
        "email": email,
        "groups": groups,
        "roles": roles,
        "claims": principal_claims,
    }

    if isinstance(name, str) and name.strip():
        principal["name"] = name.strip()

    return principal


def get_request_principal(request: Request) -> Optional[dict]:
    """
    Resolve the authenticated Microsoft Entra principal.

    Production:
        Azure App Service Easy Auth headers.

    Local development:
        Microsoft Entra Bearer access token.
    """
    easy_auth_principal = _get_easy_auth_principal(request)

    if easy_auth_principal is not None:
        return easy_auth_principal

    return _get_entra_principal(request)
