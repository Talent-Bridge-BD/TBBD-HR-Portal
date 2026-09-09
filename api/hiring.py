import base64
import json

from fastapi import APIRouter, HTTPException, Request

from repositories.hiring import SqlHiringRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context
from services.hiring import HiringService


router = APIRouter(
    prefix="/api/hiring",
    tags=["hiring"],
)

_hiring_repository = SqlHiringRepository()
_hiring_service = HiringService(
    _hiring_repository,
)
_organization_repository = SqlOrganizationRepository()


EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


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


def get_hiring_authorization_context(
    request: Request,
):
    principal_id = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL-ID"
    )
    encoded_principal = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL"
    )

    if not principal_id or not encoded_principal:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    try:
        padding = "=" * (-len(encoded_principal) % 4)
        principal = json.loads(
            base64.b64decode(
                encoded_principal + padding
            ).decode("utf-8")
        )
    except (
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated principal",
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
    context = get_hiring_authorization_context(request)

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.get("")
async def list_hiring_applications(
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    applications = _hiring_service.list_hiring_applications(
        organization_id,
    )

    return {
        "applications": [
            item.__dict__
            for item in applications
        ]
    }


@router.get("/{application_id}")
async def get_hiring_application(
    application_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    application = _hiring_service.get_hiring_application(
        organization_id,
        application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Hiring application not found",
        )

    return {
        "application": application.__dict__
    }
