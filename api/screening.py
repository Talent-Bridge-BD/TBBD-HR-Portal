from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.application import SqlApplicationRepository
from repositories.organization import SqlOrganizationRepository
from repositories.screening import SqlScreeningRepository
from services.authorization import (
    build_authorization_context_from_principal,
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


class ScreeningAssessmentRequest(BaseModel):
    basic_eligibility: str | None = None
    relevant_experience: str | None = None
    education: str | None = None
    communication: str | None = None
    availability: str | None = None
    screening_notes: str | None = None
    recommendation: str | None = None


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

    preliminary_context = build_authorization_context_from_principal(
        principal,
        [],
    )

    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not preliminary_context.roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Recruitment management role is required",
        )

    memberships = _organization_repository.get_active_memberships(
        principal_id,
    )

    return build_authorization_context_from_principal(
        principal,
        memberships,
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

    return {
        "screening": screening.__dict__,
        "message": "Screening assessment saved successfully",
    }
