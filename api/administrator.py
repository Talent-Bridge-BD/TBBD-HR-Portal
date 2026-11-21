from fastapi import APIRouter, HTTPException, Request

from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    AUTHORIZATION_GROUPS,
    build_authorization_context_from_principal,
    is_global_administrator,
)
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/administrator",
    tags=["administrator"],
)

_organization_repository = SqlOrganizationRepository()


def _get_administrator_context(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user required",
        )

    principal_id = principal["id"]

    memberships = _organization_repository.get_active_memberships(
        principal_id
    )

    context = build_authorization_context_from_principal(
        principal,
        memberships,
    )

    if not is_global_administrator(context):
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return context


@router.get("/dashboard")
def get_administrator_dashboard(request: Request):
    _get_administrator_context(request)

    # This repository method returns active organizations only.
    # It cannot provide a reliable all-organizations total.
    organizations = (
        _organization_repository.list_active_organizations()
    )

    return {
        "organizations": {
            "total": None,
            "active": len(organizations),
        },
        "users": {
            "total": None,
            "active": None,
        },
        "roles": {
            "total": len(AUTHORIZATION_GROUPS),
            "permissionSets": None,
        },
        "notifications": {
            "templates": None,
            "deliveryStatus": None,
        },
        "system": {
            "settings": None,
            "integrations": None,
            "recentActions": None,
            "failedEvents": None,
        },
    }
