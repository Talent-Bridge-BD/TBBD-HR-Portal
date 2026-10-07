from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.application import SqlApplicationRepository
from repositories.audit_logs import AuditLogRepository
from repositories.organization import SqlOrganizationRepository
from repositories.screening import SqlScreeningRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.local_auth import get_request_principal
from services.screening import ScreeningService


router = APIRouter(
    prefix="/api/screening",
    tags=["screening"],
)

_screening_repository = SqlScreeningRepository()
_screening_service = ScreeningService(
    _screening_repository,
)

_application_repository = SqlApplicationRepository()
_organization_repository = SqlOrganizationRepository()
_audit_log_repository = AuditLogRepository()


class ScreeningAssessmentRequest(BaseModel):
    basic_eligibility: str | None = None
    relevant_experience: str | None = None
    education: str | None = None
    communication: str | None = None
    availability: str | None = None
    screening_notes: str | None = None
    recommendation: str | None = None


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


@router.get("/application/{application_id}")
async def get_screening_assessment(
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

    screening = _screening_service.get_by_application(
        application_id,
    )

    return {
        "screening": (
            screening.__dict__
            if screening is not None
            else None
        )
    }


@router.put("/application/{application_id}")
async def save_screening_assessment(
    application_id: str,
    payload: ScreeningAssessmentRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )
    principal = get_request_principal(request) or {}

    application = _application_repository.get_application(
        organization_id,
        application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found for this organization",
        )

    allowed_values = {
        "basic_eligibility": {
            "Yes",
            "No",
            "Needs Review",
        },
        "relevant_experience": {
            "Strong",
            "Moderate",
            "Limited",
        },
        "education": {
            "Yes",
            "No",
            "Needs Review",
        },
        "communication": {
            "Strong",
            "Satisfactory",
            "Needs Improvement",
        },
        "availability": {
            "Immediate",
            "1 Month",
            "Later",
        },
        "recommendation": {
            "Shortlist Candidate",
            "Continue Screening",
            "Reject Application",
        },
    }

    values = {
        "basic_eligibility": payload.basic_eligibility,
        "relevant_experience": payload.relevant_experience,
        "education": payload.education,
        "communication": payload.communication,
        "availability": payload.availability,
        "recommendation": payload.recommendation,
    }

    for field, value in values.items():
        if value is not None and value not in allowed_values[field]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value for {field}: {value}",
            )

    screening = _screening_service.save(
        application_id=application_id,
        basic_eligibility=payload.basic_eligibility,
        relevant_experience=payload.relevant_experience,
        education=payload.education,
        communication=payload.communication,
        availability=payload.availability,
        screening_notes=payload.screening_notes,
        recommendation=payload.recommendation,
    )

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="screening",
        action="assessment_update",
        entity_type="application",
        entity_id=str(application_id),
        status="success",
        details={
            "candidate_id": application.candidate_id,
            "candidate_email": application.candidate_email,
            "job_id": application.job_id,
            "job_title": application.job_title,
            "basic_eligibility": screening.basic_eligibility,
            "relevant_experience": screening.relevant_experience,
            "education": screening.education,
            "communication": screening.communication,
            "availability": screening.availability,
            "recommendation": screening.recommendation,
            "screening_notes": screening.screening_notes,
        },
    )

    return {
        "screening": screening.__dict__,
        "message": "Screening assessment saved successfully",
    }
