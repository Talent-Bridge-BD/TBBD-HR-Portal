from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AuthorizationContext:
    user_id: str
    roles: frozenset[str]
    organization_ids: frozenset[str]
    is_global_administrator: bool


# Only verified, currently valid group mappings belong here.
# Employer Manager's previously reported deleted group is excluded.
AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
}

AUTHORIZATION_ROLES = frozenset({
    "Administrator",
    "HR Manager",
    "Employer Manager",
    "Candidate",
})


def normalize_role(role):
    """Normalize supported aliases while preserving unknown role names."""
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
    return bool(
        context.roles.intersection(
            normalize_role(role) for role in roles
        )
    )


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
    """Build context from verified roles and matching active memberships."""

    normalized_roles = frozenset(
        normalized
        for role in roles
        if (normalized := normalize_role(role))
    )

    organization_ids = {
        membership.organization_id
        for membership in memberships
        if (
            getattr(membership, "user_id", None) == user_id
            and getattr(membership, "status", None) == "active"
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
    """Resolve roles and groups from normalized fields and original claims."""

    user_id = principal.get("id") or ""
    roles = set(principal.get("roles") or [])
    groups = set(principal.get("groups") or [])

    for claim in principal.get("claims") or []:
        claim_type = claim.get("typ")
        claim_value = claim.get("val")
        if not claim_value:
            continue
        if claim_type == "roles":
            roles.add(claim_value)
        elif claim_type == "groups":
            groups.add(claim_value)

    for role_name, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in groups:
            roles.add(role_name)

    return build_authorization_context(
        user_id=user_id,
        roles=roles,
        memberships=memberships,
    )
