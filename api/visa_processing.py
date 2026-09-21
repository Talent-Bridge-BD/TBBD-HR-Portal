from fastapi import APIRouter, HTTPException, Request

from datetime import datetime

from repositories.application import SqlApplicationRepository
from repositories.organization import SqlOrganizationRepository
from repositories.visa_processing import SqlVisaProcessingRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.local_auth import get_request_principal
from services.visa_processing import VisaProcessingService


router = APIRouter(
    prefix="/api/visa-processing",
    tags=["visa-processing"],
)

_visa_processing_repository = SqlVisaProcessingRepository()
_visa_processing_service = VisaProcessingService(
    _visa_processing_repository,
)
_application_repository = SqlApplicationRepository()

_organization_repository = SqlOrganizationRepository()


from pydantic import BaseModel


class VisaProcessingCreateRequest(BaseModel):
    application_id: str
    test_type: str | None = None
    scheduled_at: datetime | None = None
    location: str | None = None
    assessor_name: str | None = None



class VisaProcessingAssessmentRequest(BaseModel):
    technical_knowledge_score: int
    trade_skills_score: int
    safety_awareness_score: int
    tool_handling_score: int
    communication_score: int
    problem_solving_score: int
    teamwork_score: int
    assessment_notes: str | None = None


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


def _get_authorization_context(
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
            detail="Recruitment management role is required",
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
    context = _get_authorization_context(request)

    if is_global_administrator(context):
        return context

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


@router.post("")
async def create_visa_processing(
    payload: VisaProcessingCreateRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    application = _application_repository.get_application(
        organization_id,
        payload.application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found for this organization",
        )

    try:
        visa_processing = _visa_processing_service.create(
            application_id=payload.application_id,
            test_type=payload.test_type,
            scheduled_at=payload.scheduled_at,
            location=payload.location,
            assessor_name=payload.assessor_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "visa_processing": visa_processing.__dict__
    }


@router.get("/application/{application_id}")
async def list_visa_processings(
    application_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    application = _application_repository.get_application(
        organization_id,
        application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found for this organization",
        )

    tests = _visa_processing_service.list_by_application(
        application_id,
    )

    return {
        "visa_processings": [
            item.__dict__
            for item in tests
        ]
    }


@router.get("/{visa_processing_id}")
async def get_visa_processing(
    visa_processing_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    visa_processing = _visa_processing_service.get(
        visa_processing_id,
    )

    if visa_processing is None:
        raise HTTPException(
            status_code=404,
            detail="Trade test not found",
        )

    application = _application_repository.get_application(
        organization_id,
        visa_processing.application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Trade test not found",
        )

    return {
        "visa_processing": visa_processing.__dict__
    }

@router.put("/{visa_processing_id}/assessment")
async def update_visa_processing_assessment(
    visa_processing_id: str,
    payload: VisaProcessingAssessmentRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    visa_processing = _visa_processing_service.get(
        visa_processing_id,
    )

    if visa_processing is None:
        raise HTTPException(
            status_code=404,
            detail="Trade test not found",
        )

    application = _application_repository.get_application(
        organization_id,
        visa_processing.application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Trade test not found",
        )

    updated = _visa_processing_service.update_assessment(
        visa_processing_id=visa_processing_id,
        technical_knowledge_score=payload.technical_knowledge_score,
        trade_skills_score=payload.trade_skills_score,
        safety_awareness_score=payload.safety_awareness_score,
        tool_handling_score=payload.tool_handling_score,
        communication_score=payload.communication_score,
        problem_solving_score=payload.problem_solving_score,
        teamwork_score=payload.teamwork_score,
        assessment_notes=payload.assessment_notes,
    )

    return {
        "visa_processing": updated.__dict__
    }

