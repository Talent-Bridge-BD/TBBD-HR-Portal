from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AuthorizationContext:

    user_id: str

    roles: frozenset[str]

    organization_ids: frozenset[str]

    is_global_administrator: bool


AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}


def has_role(context: AuthorizationContext, role: str) -> bool:

    return role in context.roles


def is_global_administrator(context: AuthorizationContext) -> bool:

    return context.is_global_administrator


def has_any_role(
    context: AuthorizationContext,
    roles: Iterable[str],
) -> bool:

    return bool(context.roles.intersection(roles))


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
    """Build authorization context using verified user roles and memberships."""

    normalized_roles = frozenset(
        normalize_role(role)
        for role in roles
        if normalize_role(role)
    )

    # Organization scope is limited to active memberships matching
    # an explicitly assigned HR Manager or Employer Manager role.
    # Membership alone cannot elevate a user's role.
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

 pr20-conflict-resolution-20261117


    role_aliases = {
        "HR.Manager": "HR Manager",
    }
    normalized_roles = frozenset(
        role_aliases.get(role, role) for role in roles
    )

 main
    return AuthorizationContext(
        user_id=user_id,
        roles=normalized_roles,
        organization_ids=frozenset(organization_ids),
        is_global_administrator="Administrator" in normalized_roles,
    )


 pr20-conflict-resolution-20261117
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




def build_authorization_context_from_principal(
    principal: dict,
    memberships: Iterable[object],
) -> AuthorizationContext:
    user_id = principal.get("id") or ""
    roles = set(principal.get("roles") or [])
    groups = set(principal.get("groups") or [])

    for role_name, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in groups:
            roles.add(role_name)

    return build_authorization_context(
        user_id=user_id,
        roles=roles,
        memberships=memberships,
    )
main
