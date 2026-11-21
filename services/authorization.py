from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AuthorizationContext:
    user_id: str
    roles: frozenset[str]
    organization_ids: frozenset[str]
    is_global_administrator: bool


# These are the only verified internal Tenant 1 group mappings.
# External Candidate and Employer roles must be established through
# validated external identity claims or application-managed assignments.
AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
}


def normalize_role(role):
    """Normalize known role aliases while preserving unknown role names."""
    if role is None:
        return ""

    value = str(role).strip()
    if not value:
        return ""

    aliases = {
        "hr.manager": "HR Manager",
        "employer.manager": "Employer Manager",
    }
    return aliases.get(value.casefold(), value)


def has_role(context: AuthorizationContext, role: str) -> bool:
    return normalize_role(role) in context.roles


def is_global_administrator(context: AuthorizationContext) -> bool:
    return context.is_global_administrator


def has_any_role(
    context: AuthorizationContext,
    roles: Iterable[str],
) -> bool:
    return bool(context.roles.intersection(
        normalize_role(role) for role in roles
    ))


def has_organization_access(
    context: AuthorizationContext,
    organization_id: str,
) -> bool:
    if is_global_administrator(context):
        return True
    return organization_id in context.organization_ids


def require_role(context: AuthorizationContext, role: str) -> None:
    if not has_role(context, role):
        raise PermissionError(f"Required role: {role}")


def require_organization_access(
    context: AuthorizationContext,
    organization_id: str,
) -> None:
    if not has_organization_access(context, organization_id):
        raise PermissionError(
            f"User is not authorized for organization: {organization_id}"
        )


def build_authorization_context(
    user_id: str,
    roles: Iterable[str],
    memberships: Iterable[object],
) -> AuthorizationContext:
    """Build authorization context from verified roles and active memberships."""

    normalized_roles = frozenset(
        normalized
        for role in roles
        if (normalized := normalize_role(role))
    )

    organization_ids = {
        membership.organization_id
        for membership in memberships
        if (
            membership.user_id == user_id
            and membership.status == "active"
            and normalize_role(getattr(membership, "role", ""))
            in {"HR Manager", "Employer Manager"}
            and normalize_role(getattr(membership, "role", ""))
            in normalized_roles
        )
    }

    return AuthorizationContext(
        user_id=user_id,
        roles=normalized_roles,
        organization_ids=frozenset(organization_ids),
        is_global_administrator="Administrator" in normalized_roles,
    )


def build_authorization_context_from_principal(
    principal: dict,
    memberships: Iterable[object],
) -> AuthorizationContext:
    """Build context from the normalized authenticated principal."""

    user_id = principal.get("id") or ""
    roles = {
        normalize_role(role)
        for role in (principal.get("roles") or [])
        if normalize_role(role)
    }
    groups = set(principal.get("groups") or [])

    for role_name, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in groups:
            roles.add(role_name)

    return build_authorization_context(
        user_id=user_id,
        roles=roles,
        memberships=memberships,
    )
