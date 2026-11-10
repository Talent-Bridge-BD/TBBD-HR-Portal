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

    def _claim_values(*claim_types):
        values = []
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            claim_type = str(claim.get("typ", "")).lower()
            claim_type = claim_type.rsplit("/", 1)[-1].rsplit(":", 1)[-1]
            value = claim.get("val")
            if claim_type in claim_types and isinstance(value, str) and value.strip():
                values.append(value.strip())
        return values

    principal["groups"] = _claim_values("groups")
    principal["roles"] = _claim_values("roles", "role")

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

    email_claim = None
    for claim_type in ("preferred_username", "email", "emails", "upn"):
        email_claim = next(
            (
                claim["val"].strip()
                for claim in claims
                if isinstance(claim, dict)
                and str(claim.get("typ", "")).lower() == claim_type
                and isinstance(claim.get("val"), str)
                and "@" in claim["val"].strip()
            ),
            None,
        )
        if email_claim:
            break

    header_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    principal["email"] = email_claim or (
        header_name.strip()
        if header_name and "@" in header_name
        else None
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
    Resolve the authenticated identity without mixing authentication sessions.

    A supplied Authorization header is authoritative:
    - A valid Bearer token resolves to the workforce identity.
    - An invalid or unsupported Authorization header is rejected.
    - It never falls back to an Easy Auth cookie identity.

    Easy Auth is used only when no Authorization header is supplied.
    """
    authorization = request.headers.get("Authorization")

    if authorization is not None:
        scheme, separator, token = authorization.partition(" ")

        if (
            scheme.lower() != "bearer"
            or not separator
            or not token.strip()
        ):
            return None

        return _get_entra_principal(request)

    return _get_easy_auth_principal(request)
