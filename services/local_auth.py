import base64
import json
from typing import Optional

import jwt
import requests
from fastapi import Request


TBBD_TENANT_ID = "319c9d59-c5f1-48d3-af49-4f959b5e02c1"
TBBD_CLIENT_ID = "16835108-56db-49f8-a566-a52bc0691cec"
TBBD_EXTERNAL_ID_TENANT_ID = "c8573333-aad0-4a28-8e40-c20e17989f61"

# Microsoft Entra ID authority endpoints.
# Build the URLs from separate strings to avoid Markdown-link corruption.
ENTRA_ISSUER = (
    "https://" + "login.microsoftonline.com/"
    + TBBD_TENANT_ID + "/v2.0"
)

ENTRA_JWKS_URL = (
    "https://" + "login.microsoftonline.com/"
    + TBBD_TENANT_ID + "/discovery/v2.0/keys"
)


def _get_easy_auth_principal(request: Request) -> Optional[dict]:
    """Read the authenticated principal supplied by Azure App Service Easy Auth."""
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    encoded_principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not principal_id or not encoded_principal:
        return None

    try:
        padding = "=" * (-len(encoded_principal) % 4)
        decoded = base64.b64decode(
            encoded_principal + padding,
            validate=True,
        )
        principal = json.loads(decoded.decode("utf-8"))

        if not isinstance(principal, dict):
            return None

    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    claims = principal.get("claims", [])
    if not isinstance(claims, list):
        claims = []

    tenant_id = next(
        (
            str(claim.get("val"))
            for claim in claims
            if isinstance(claim, dict)
            and (
                str(claim.get("typ", "")).lower().endswith("tenantid")
                or str(claim.get("typ", "")).lower() == "tid"
            )
            and claim.get("val")
        ),
        None,
    )

    principal["tenant_id"] = tenant_id
    principal["id"] = principal_id
    principal["email"] = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL-NAME"
    )

    name_claim = next(
        (
            str(claim.get("val"))
            for claim in claims
            if isinstance(claim, dict)
            and str(claim.get("typ", "")).lower() in ("name", "displayname")
            and claim.get("val")
        ),
        None,
    )

    if name_claim:
        principal["name"] = name_claim

    return principal


def _get_bearer_token(request: Request) -> Optional[str]:
    """Extract a bearer token from the Authorization header."""
    authorization = request.headers.get("Authorization", "")

    scheme, separator, token = authorization.partition(" ")

    if not separator or scheme.lower() != "bearer":
        return None

    token = token.strip()
    return token or None


def _get_entra_principal(request: Request) -> Optional[dict]:
    """Validate a Microsoft Entra access token and build a principal."""
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
            options={
                "require": ["exp", "iat"],
            },
        )

    except (
        jwt.PyJWTError,
        requests.RequestException,
        ValueError,
    ):
        return None

    principal_id = claims.get("oid")
    tenant_id = claims.get("tid")

    if not principal_id or not tenant_id:
        return None

    email = (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or ""
    )

    groups = claims.get("groups", [])
    roles = claims.get("roles", [])

    if not isinstance(groups, list):
        groups = []

    if not isinstance(roles, list):
        roles = []

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
            {"typ": "oid", "val": str(principal_id)},
            {"typ": "tid", "val": str(tenant_id)},
        ]
    )

    principal = {
        "id": str(principal_id),
        "tenant_id": str(tenant_id),
        "email": str(email),
        "groups": groups,
        "roles": roles,
        "claims": principal_claims,
    }

    if claims.get("name"):
        principal["name"] = str(claims["name"])

    return principal


def get_request_principal(request: Request) -> Optional[dict]:
    """
    Resolve the authenticated Microsoft Entra principal.

    Production:
        Azure App Service Easy Auth headers.

    Local development:
        Microsoft Entra bearer access token.
    """
    easy_auth_principal = _get_easy_auth_principal(request)

    if easy_auth_principal:
        return easy_auth_principal

    return _get_entra_principal(request)
