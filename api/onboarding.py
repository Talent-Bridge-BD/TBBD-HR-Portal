from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from repositories.application import SqlApplicationRepository
from repositories.audit_logs import AuditLogRepository
from repositories.medical_examination import SqlMedicalExaminationRepository
from repositories.onboarding import SqlOnboardingRepository
from repositories.ticketing import SqlTicketingRepository
from repositories.visa_processing import SqlVisaProcessingRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.deployment_readiness import DeploymentReadinessService
from services.local_auth import get_request_principal
from services.onboarding import OnboardingService


router = APIRouter(
    prefix="/api/onboarding",
    tags=["onboarding"],
)

_onboarding_repository = SqlOnboardingRepository()
_onboarding_service = OnboardingService(
    _onboarding_repository,
)

_application_repository = SqlApplicationRepository()
_organization_repository = SqlOrganizationRepository()
_medical_repository = SqlMedicalExaminationRepository()
_visa_repository = SqlVisaProcessingRepository()
_ticketing_repository = SqlTicketingRepository()
_deployment_readiness_service = DeploymentReadinessService(
    onboarding_repository=_onboarding_repository,
    medical_repository=_medical_repository,
    visa_repository=_visa_repository,
    ticketing_repository=_ticketing_repository,
)
_audit_log_repository = AuditLogRepository()


class OnboardingCreateRequest(BaseModel):
    application_id: str
    employer_name: str | None = None
    job_title: str | None = None
    joining_date: date | None = None
    status: str = "Pending"
    contract_signed: bool = False
    documents_verified: bool = False
    orientation_completed: bool = False
    accommodation_arranged: bool = False
    transport_arranged: bool = False
    notes: str | None = None


class OnboardingUpdateRequest(BaseModel):
    employer_name: str | None = None
    job_title: str | None = None
    joining_date: date | None = None
    status: str | None = None
    contract_signed: bool | None = None
    documents_verified: bool | None = None
    orientation_completed: bool | None = None
    accommodation_arranged: bool | None = None
    transport_arranged: bool | None = None
    notes: str | None = None
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


def _require_organization_write_access(
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
async def create_onboarding(
    payload: OnboardingCreateRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_write_access(
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

    if payload.status == "Completed":
        readiness = _deployment_readiness_service.check(
            organization_id=organization_id,
            application_id=payload.application_id,
            destination_country=application.destination_country,
            target_onboarding_status="Completed",
        )

        if not readiness["ready"]:
            next_step = readiness["next_step"] or "Complete the required workflow steps."
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "DEPLOYMENT_NOT_READY",
                    "message": (
                        "Onboarding cannot be marked as Completed yet. "
                        f"Next step: {next_step}."
                    ),
                    "prerequisites": readiness["prerequisites"],
                    "next_step": next_step,
                },
            )

    try:
        onboarding = _onboarding_service.create(
            application_id=payload.application_id,
            employer_name=payload.employer_name,
            job_title=payload.job_title,
            joining_date=payload.joining_date,
            status=payload.status,
            contract_signed=payload.contract_signed,
            documents_verified=payload.documents_verified,
            orientation_completed=payload.orientation_completed,
            accommodation_arranged=payload.accommodation_arranged,
            transport_arranged=payload.transport_arranged,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    principal = get_request_principal(request) or {}

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="onboarding",
        action="create",
        entity_type="onboarding",
        entity_id=str(onboarding.id),
        status="success",
        details={
            "application_id": str(payload.application_id),
        },
    )

    return {
        "onboarding": onboarding.__dict__
    }


@router.get("/application/{application_id}")
async def list_onboarding_by_application(
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

    onboarding_records = _onboarding_service.list_by_application(
        application_id,
    )

    return {
        "onboarding": [
            item.__dict__
            for item in onboarding_records
        ]
    }


@router.get("/{onboarding_id}")
async def get_onboarding(
    onboarding_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    onboarding = _onboarding_service.get(
        onboarding_id,
    )

    if onboarding is None:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    application = _application_repository.get_application(
        organization_id,
        onboarding.application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    return {
        "onboarding": onboarding.__dict__
    }


@router.put("/{onboarding_id}")
async def update_onboarding(
    onboarding_id: str,
    payload: OnboardingUpdateRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_write_access(
        request,
        organization_id,
    )

    onboarding = _onboarding_service.get(
        onboarding_id,
    )

    if onboarding is None:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    application = _application_repository.get_application(
        organization_id,
        onboarding.application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Onboarding record not found",
        )

    if payload.status == "Completed":
        readiness = _deployment_readiness_service.check(
            organization_id=organization_id,
            application_id=onboarding.application_id,
            destination_country=application.destination_country,
            target_onboarding_status="Completed",
        )

        if not readiness["ready"]:
            next_step = readiness["next_step"] or "Complete the required workflow steps."
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "DEPLOYMENT_NOT_READY",
                    "message": (
                        "Onboarding cannot be marked as Completed yet. "
                        f"Next step: {next_step}."
                    ),
                    "prerequisites": readiness["prerequisites"],
                    "next_step": next_step,
                },
            )

    try:
        updated = _onboarding_service.update(
            onboarding_id=onboarding_id,
            employer_name=payload.employer_name,
            job_title=payload.job_title,
            joining_date=payload.joining_date,
            status=payload.status,
            contract_signed=payload.contract_signed,
            documents_verified=payload.documents_verified,
            orientation_completed=payload.orientation_completed,
            accommodation_arranged=payload.accommodation_arranged,
            transport_arranged=payload.transport_arranged,
            notes=payload.notes,
            completed_at=payload.completed_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    principal = get_request_principal(request) or {}

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="onboarding",
        action="update",
        entity_type="onboarding",
        entity_id=str(onboarding_id),
        status="success",
        details={
            "application_id": str(onboarding.application_id),
            "previous_status": getattr(onboarding, "status", None),
            "new_status": (
                payload.status
                if payload.status is not None
                else getattr(onboarding, "status", None)
            ),
        },
    )

    return {
        "onboarding": updated.__dict__
    }
