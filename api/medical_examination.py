from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.application import SqlApplicationRepository
from repositories.organization import SqlOrganizationRepository
from repositories.medical_examination import SqlMedicalExaminationRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.local_auth import get_request_principal
from services.medical_examination import MedicalExaminationService


router = APIRouter(
    prefix="/api/medical-examinations",
    tags=["medical-examinations"],
)

_medical_examination_repository = SqlMedicalExaminationRepository()

_medical_examination_service = MedicalExaminationService(
    _medical_examination_repository,
)

_application_repository = SqlApplicationRepository()
_organization_repository = SqlOrganizationRepository()


class MedicalExaminationCreateRequest(BaseModel):
    application_id: str
    medical_center: str | None = None
    examination_date: datetime | None = None
    doctor_name: str | None = None
    medical_type: str | None = None


class MedicalExaminationAssessmentRequest(BaseModel):
    medical_center: str | None = None
    examination_date: datetime | None = None
    doctor_name: str | None = None
    medical_type: str | None = None
    status: str
    result: str
    report_notes: str | None = None
    completed_at: datetime | None = None


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

    group_ids = _claim_values(
        claims,
        "groups",
    )

    token_roles = _claim_values(
        claims,
        "roles",
    )

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
async def create_medical_examination(
    payload: MedicalExaminationCreateRequest,
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
        medical_examination = _medical_examination_service.create(
            organization_id=organization_id,
            application_id=payload.application_id,
            medical_center=payload.medical_center,
            examination_date=payload.examination_date,
            doctor_name=payload.doctor_name,
            medical_type=payload.medical_type,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "medical_examination": medical_examination.__dict__
    }


@router.get("/application/{application_id}")
async def list_medical_examinations(
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

    examinations = _medical_examination_service.list_by_application(
        organization_id,
        application_id,
    )

    return {
        "medical_examinations": [
            item.__dict__
            for item in examinations
        ]
    }


@router.get("/{medical_examination_id}")
async def get_medical_examination(
    medical_examination_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    medical_examination = _medical_examination_service.get(
        organization_id,
        medical_examination_id,
    )

    if medical_examination is None:
        raise HTTPException(
            status_code=404,
            detail="Medical examination not found",
        )

    application = _application_repository.get_application(
        organization_id,
        medical_examination.application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Medical examination not found",
        )

    return {
        "medical_examination": medical_examination.__dict__
    }


@router.put("/{medical_examination_id}/assessment")
async def update_medical_examination_assessment(
    medical_examination_id: str,
    payload: MedicalExaminationAssessmentRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    medical_examination = _medical_examination_service.get(
        organization_id,
        medical_examination_id,
    )

    if medical_examination is None:
        raise HTTPException(
            status_code=404,
            detail="Medical examination not found",
        )

    application = _application_repository.get_application(
        organization_id,
        medical_examination.application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Medical examination not found",
        )

    try:
        updated = _medical_examination_service.update_assessment(
            organization_id=organization_id,
            medical_examination_id=medical_examination_id,
            medical_center=payload.medical_center,
            examination_date=payload.examination_date,
            doctor_name=payload.doctor_name,
            medical_type=payload.medical_type,
            status=payload.status,
            result=payload.result,
            report_notes=payload.report_notes,
            completed_at=payload.completed_at,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "medical_examination": updated.__dict__
    }
