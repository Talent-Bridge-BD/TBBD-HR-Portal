import base64
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.interview import SqlInterviewRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import build_authorization_context
from services.interview import InterviewService


router = APIRouter(
    prefix="/api/interviews",
    tags=["interviews"],
)

_interview_repository = SqlInterviewRepository()
_interview_service = InterviewService(
    _interview_repository,
)
_organization_repository = SqlOrganizationRepository()


EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


class InterviewRequest(BaseModel):
    application_id: str
    scheduled_start: datetime
    scheduled_end: datetime | None = None
    interview_type: str = ""
    location_or_link: str = ""
    interviewer_name: str = ""
    notes: str = ""


class InterviewUpdateRequest(BaseModel):
    scheduled_start: datetime
    scheduled_end: datetime | None = None
    interview_type: str = ""
    location_or_link: str = ""
    interviewer_name: str = ""
    notes: str = ""
    status: str = "scheduled"


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


def get_interview_authorization_context(
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
    context = get_interview_authorization_context(request)

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.get("")
async def list_interviews(
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    interviews = _interview_service.list_interviews(
        organization_id,
    )

    return {
        "interviews": [
            item.__dict__
            for item in interviews
        ]
    }


@router.get("/{interview_id}")
async def get_interview(
    interview_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    interview = _interview_service.get_interview(
        organization_id,
        interview_id,
    )

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    return {
        "interview": interview.__dict__
    }


@router.post("")
async def create_interview(
    payload: InterviewRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    try:
        interview = _interview_service.create_interview(
            organization_id=organization_id,
            application_id=payload.application_id,
            scheduled_start=payload.scheduled_start,
            scheduled_end=payload.scheduled_end,
            interview_type=payload.interview_type,
            location_or_link=payload.location_or_link,
            interviewer_name=payload.interviewer_name,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "interview": interview.__dict__
    }


@router.put("/{interview_id}")
async def update_interview(
    interview_id: str,
    payload: InterviewUpdateRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    allowed_statuses = {
        "scheduled",
        "completed",
        "cancelled",
        "rescheduled",
        "no_show",
    }

    if payload.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid interview status",
        )

    interview = _interview_service.update_interview(
        organization_id=organization_id,
        interview_id=interview_id,
        scheduled_start=payload.scheduled_start,
        scheduled_end=payload.scheduled_end,
        interview_type=payload.interview_type,
        location_or_link=payload.location_or_link,
        interviewer_name=payload.interviewer_name,
        notes=payload.notes,
        status=payload.status,
    )

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    return {
        "interview": interview.__dict__
    }
