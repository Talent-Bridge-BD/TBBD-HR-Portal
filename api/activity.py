from fastapi import APIRouter, HTTPException, Query, Request

from repositories.audit_logs import AuditLogRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/activity",
    tags=["activity"],
)


_audit_log_repository = AuditLogRepository()
_organization_repository = SqlOrganizationRepository()


AUTHORIZATION_GROUPS = {
    "Administrator": "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66",
    "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
    "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
    "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
}


def _get_activity_context(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user required",
        )

    principal_id = principal["id"]
    claims = principal.get("claims", [])

    group_ids = {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == "groups"
        and claim.get("val")
    }

    roles_claim = {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == "roles"
        and claim.get("val")
    }

    roles = set(roles_claim)

    for role_name, group_id in AUTHORIZATION_GROUPS.items():
        if group_id in group_ids:
            roles.add(role_name)

    allowed_roles = {
        "Administrator",
        "HR Manager",
        "Employer Manager",
    }

    if not roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Workplace activity access required",
        )

    memberships = _organization_repository.get_active_memberships(
        principal_id
    )

    return build_authorization_context(
        user_id=principal_id,
        roles=roles,
        memberships=memberships,
    )


@router.get("")
def get_workplace_activity(
    request: Request,
    limit: int = Query(default=3, ge=1, le=10),
):
    context = _get_activity_context(request)

    if is_global_administrator(context):
        activities = _audit_log_repository.list_recent(limit=limit)
    else:
        activities = _audit_log_repository.list_recent_for_organizations(
            organization_ids=context.organization_ids,
            limit=limit,
        )

    return {
        "activities": activities,
    }
