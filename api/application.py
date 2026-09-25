import base64
import json

from fastapi import APIRouter, HTTPException, Request

from repositories.application import SqlApplicationRepository
from repositories.organization import SqlOrganizationRepository
from services.application import ApplicationService
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/applications",
    tags=["applications"],
)

_application_repository = SqlApplicationRepository()
_application_service = ApplicationService(
    _application_repository,
)
_organization_repository = SqlOrganizationRepository()


EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"


def _claim_values(
    claims: list[dict],
    claim_type: str,
) -> set[str]:
    return {
        str(claim.get("val"))
        for claim in claims
        if claim.get("typ") == claim_type
        and claim.get("val")
    }


def get_application_authorization_context(
    request: Request,
):
    principal = get_request_principal(request)

    if not principal:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    principal_id = principal.get("id")

    if not principal_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    claims = principal.get("claims", [])
    group_ids = _claim_values(claims, "groups")
    token_roles = _claim_values(claims, "roles")

    roles = set(token_roles)

    if EMPLOYER_MANAGER_GROUP_ID in group_ids:
        roles.add("Employer Manager")

    if HR_MANAGER_GROUP_ID in group_ids:
        roles.add("HR Manager")

    if ADMINISTRATOR_GROUP_ID in group_ids:
        roles.add("Administrator")

    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Employer management role is required",
        )

    memberships = _organization_repository.get_active_memberships(
        principal_id,
    )

    return build_authorization_context(
        user_id=principal_id,
        roles=roles,
        memberships=memberships,
    )

def _require_organization_access(
    request: Request,
    organization_id: str,
):
    context = get_application_authorization_context(request)

    if is_global_administrator(context):
        return context

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.get("")
async def list_applications(
    request: Request,
    organization_id: str | None = None,
):
    context = get_application_authorization_context(request)

    if is_global_administrator(context) and not organization_id:
        applications = _application_service.list_all_active_organization_applications()
    else:
        if not organization_id:
            raise HTTPException(
                status_code=400,
                detail="organization_id is required",
            )

        _require_organization_access(
            request,
            organization_id,
        )

        applications = _application_service.list_applications(
            organization_id,
        )

    return {
        "applications": [
            item.__dict__
            for item in applications
        ]
    }


@router.put("/{application_id}/status")
async def update_application_status(
    application_id: str,
    organization_id: str,
    status: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )
    allowed_statuses = {
        "submitted",
        "under_review",
        "shortlisted",
        "interview",
        "offer",
        "hired",
        "rejected",
    }

    normalized_status = status.strip().lower()

    if normalized_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid application status: {status}",
        )

    application = _application_service.update_status(
        organization_id,
        application_id,
        normalized_status,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return {
        "application": application.__dict__,
        "message": "Application status updated successfully",
    }


@router.get("/{application_id}")
async def get_application(
    application_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    application = _application_service.get_application(
        organization_id,
        application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return {
        "application": application.__dict__
    }
