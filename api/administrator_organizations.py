from fastapi import APIRouter, Request, HTTPException

from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/administrator/organizations",
    tags=["administrator-organizations"],
)

_repository = SqlOrganizationRepository()


AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}


def require_admin(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user required",
        )

    groups = principal.get("groups") or []
    roles_claim = principal.get("roles") or []
    roles = set(roles_claim)

    for role_name, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in groups:
            roles.add(role_name)

    context = build_authorization_context(
        user_id=principal["id"],
        roles=roles,
        memberships=_repository.get_active_memberships(
            principal["id"]
        ),
    )

    if not is_global_administrator(context):
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return context


@router.get("")
def list_organizations(request: Request):

    require_admin(request)

    organizations = _repository.list_active_organizations()

    return {
        "organizations": [
            {
                "id": organization.id,
                "name": organization.name,
                "status": organization.status,
            }
            for organization in organizations
        ]
    }
