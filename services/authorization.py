from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AuthorizationContext:
    user_id: str
    roles: frozenset[str]
    organization_ids: frozenset[str]


def has_role(context: AuthorizationContext, role: str) -> bool:
    return role in context.roles


def has_any_role(
    context: AuthorizationContext,
    roles: Iterable[str],
) -> bool:
    return bool(context.roles.intersection(roles))


def has_organization_access(
    context: AuthorizationContext,
    organization_id: str,
) -> bool:
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
    organization_ids = frozenset(
        membership.organization_id
        for membership in memberships
        if (
            membership.user_id == user_id
            and membership.status == "active"
        )
    )

    return AuthorizationContext(
        user_id=user_id,
        roles=frozenset(roles),
        organization_ids=organization_ids,
    )
