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


def require_admin(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user required",
        )

    roles = set(principal.get("roles") or [])

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
