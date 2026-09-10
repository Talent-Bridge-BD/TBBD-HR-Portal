import base64
import json
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.onboarding import SqlOnboardingRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context
from services.onboarding import OnboardingService


router = APIRouter(
    prefix="/api/recruitment/onboarding",
    tags=["recruitment-onboarding"],
)

_onboarding_repository = SqlOnboardingRepository()
_onboarding_service = OnboardingService(
    _onboarding_repository,
)
_organization_repository = SqlOrganizationRepository()


EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


ALLOWED_STATUSES = {
    "pending",
    "in_progress",
    "completed",
    "cancelled",
}


ALLOWED_TRANSITIONS = {
    "pending": {
        "pending",
        "in_progress",
        "cancelled",
    },
    "in_progress": {
        "in_progress",
        "completed",
        "cancelled",
    },
    "completed": {
        "completed",
    },
    "cancelled": {
        "cancelled",
    },
}


class CreateOnboardingRequest(BaseModel):
    application_id: str
    status: str = "pending"
    planned_start_date: Optional[date] = None
    employment_type: Optional[str] = None
    notes: Optional[str] = None


class UpdateOnboardingRequest(BaseModel):
    status: str
    planned_start_date: Optional[date] = None
    employment_type: Optional[str] = None
    notes: Optional[str] = None


def _claim_values(
    principal: dict,
    claim_type: str,
) -> list[str]:
    values = []

    for claim in principal.get("claims", []):
        if claim.get("typ") == claim_type:
            value = claim.get("val")
            if value:
                values.append(value)

    return values


def get_onboarding_authorization_context(
    request: Request,
):
    principal_id = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL-ID"
    )
    principal_header = request.headers.get(
        "X-MS-CLIENT-PRINCIPAL"
    )

    if not principal_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    if not principal_header:
        raise HTTPException(
            status_code=401,
            detail="Authenticated principal is required",
        )

    try:
        padding = "=" * (-len(principal_header) % 4)
        principal = json.loads(
            base64.b64decode(
                principal_header + padding
            ).decode("utf-8")
        )
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated principal",
        ) from exc

    groups = set(
        _claim_values(
            principal,
            "groups",
        )
    )

    token_roles = set(
        _claim_values(
            principal,
            "roles",
        )
    )

    roles = set(token_roles)

    if EMPLOYER_MANAGER_GROUP_ID in groups:
        roles.add("Employer Manager")

    if HR_MANAGER_GROUP_ID in groups:
        roles.add("HR Manager")

    if ADMINISTRATOR_GROUP_ID in groups:
        roles.add("Administrator")

    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for recruitment onboarding",
        )

    memberships = _organization_repository.get_active_memberships(
        principal_id
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
    context = get_onboarding_authorization_context(
        request
    )

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.get("")
def list_onboarding(
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    onboarding = _onboarding_service.list_onboarding(
        organization_id,
    )

    return {
        "onboarding": [
            item.__dict__
            for item in onboarding
        ]
    }


@router.get("/{onboarding_id}")
def get_onboarding(
    onboarding_id: str,
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    onboarding = _onboarding_service.get_onboarding(
        organization_id,
        onboarding_id,
    )

    if onboarding is None:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    return {
        "onboarding": onboarding.__dict__
    }


@router.post("")
def create_onboarding(
    payload: CreateOnboardingRequest,
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    if payload.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid onboarding status",
        )

    try:
        onboarding = _onboarding_service.create_onboarding(
            organization_id=organization_id,
            application_id=payload.application_id,
            status=payload.status,
            planned_start_date=payload.planned_start_date,
            employment_type=payload.employment_type,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "onboarding": onboarding.__dict__
    }


@router.put("/{onboarding_id}")
def update_onboarding(
    onboarding_id: str,
    payload: UpdateOnboardingRequest,
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    if payload.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid onboarding status",
        )

    current = _onboarding_service.get_onboarding(
        organization_id,
        onboarding_id,
    )

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    allowed_next_statuses = ALLOWED_TRANSITIONS.get(
        current.status,
        set(),
    )

    if payload.status not in allowed_next_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid onboarding status transition: "
                f"{current.status} -> {payload.status}"
            ),
        )

    try:
        onboarding = _onboarding_service.update_onboarding(
            organization_id=organization_id,
            onboarding_id=onboarding_id,
            status=payload.status,
            planned_start_date=payload.planned_start_date,
            employment_type=payload.employment_type,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if onboarding is None:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    return {
        "onboarding": onboarding.__dict__
    }


@router.delete("/{onboarding_id}")
def delete_onboarding(
    onboarding_id: str,
    request: Request,
    organization_id: str,
):
    _require_organization_access(
        request,
        organization_id,
    )

    deleted = _onboarding_service.delete_onboarding(
        organization_id,
        onboarding_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    return {
        "deleted": True,
        "id": onboarding_id,
    }
