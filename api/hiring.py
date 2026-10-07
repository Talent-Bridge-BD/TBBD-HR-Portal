from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from repositories.audit_logs import AuditLogRepository
from repositories.hiring import SqlHiringRepository
from repositories.organization import SqlOrganizationRepository
from services.authorization import (
    build_authorization_context,
    is_global_administrator,
)
from services.hiring import HiringService
from services.notification_service import NotificationService
from services.local_auth import get_request_principal
from services.offer_letter import generate_offer_letter


router = APIRouter(
    prefix="/api/hiring",
    tags=["hiring"],
)

_hiring_repository = SqlHiringRepository()
_hiring_service = HiringService(
    _hiring_repository,
)
_organization_repository = SqlOrganizationRepository()
_audit_log_repository = AuditLogRepository()


EMPLOYER_MANAGER_GROUP_ID = "7088ce1f-8e01-4c7c-88fd-a257721a35df"
HR_MANAGER_GROUP_ID = "9a977cf0-7c9f-4024-9415-357a8a4292bc"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"


class HiringReadyRequest(BaseModel):
    readiness_source: str
    waiver_reason: Optional[str] = None


class HiringOfferRequest(BaseModel):
    offer_title: str
    employment_type: Optional[str] = None
    salary_amount: Optional[float] = None
    salary_currency: Optional[str] = None
    start_date: Optional[date] = None
    offer_expiry_date: Optional[date] = None
    terms_and_conditions: Optional[str] = None


class HiringOfferUpdateRequest(BaseModel):
    offer_title: Optional[str] = None
    employment_type: Optional[str] = None
    salary_amount: Optional[float] = None
    salary_currency: Optional[str] = None
    start_date: Optional[date] = None
    offer_expiry_date: Optional[date] = None
    terms_and_conditions: Optional[str] = None
    status: str


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

    if is_global_administrator(context):
        return context

    if organization_id not in context.organization_ids:
        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this organization",
        )

    return context


def _handle_service_error(error: ValueError):
    message = str(error)

    if "not found" in message.lower():
        raise HTTPException(
            status_code=404,
            detail=message,
        )

    raise HTTPException(
        status_code=400,
        detail=message,
    )


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


@router.get("/ready")
async def list_ready_for_hiring(
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    applications = _hiring_service.list_ready_for_hiring(
        organization_id,
    )

    return {
        "applications": [
            item.__dict__
            for item in applications
        ]
    }


@router.get("/{application_id}/offer/{offer_id}/letter")
async def preview_offer_letter(
    application_id: str,
    offer_id: str,
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

    offer = _hiring_service.get_offer(
        organization_id,
        application_id,
        offer_id,
    )

    if offer is None:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    organizations = _organization_repository.list_active_organizations()
    organization = next(
        (
            item
            for item in organizations
            if item.id == organization_id
        ),
        None,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    pdf_bytes = generate_offer_letter(
        organization_name=organization.name,
        application=application,
        offer=offer,
    )

    candidate_name = "candidate"
    candidate_parts = [
        application.candidate_first_name,
        application.candidate_last_name,
    ]
    candidate_name = "-".join(
        part.strip().lower()
        for part in candidate_parts
        if part and part.strip()
    ) or "candidate"

    filename = f"offer-letter-{candidate_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'inline; filename="{filename}"'
            )
        },
    )


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

    hiring_record = _hiring_service.get_hiring_record(
        organization_id,
        application_id,
    )

    readiness = _hiring_service.get_readiness(
        organization_id,
        application_id,
    )

    return {
        "application": application.__dict__,
        "hiring_record": hiring_record,
        "readiness": readiness,
    }


@router.get("/{application_id}/readiness")
async def get_hiring_readiness(
    application_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    readiness = _hiring_service.get_readiness(
        organization_id,
        application_id,
    )

    if readiness is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    hiring_record = _hiring_service.get_hiring_record(
        organization_id,
        application_id,
    )

    return {
        "readiness": readiness,
        "hiring_record": hiring_record,
    }


@router.post("/{application_id}/ready")
async def mark_ready_for_hiring(
    application_id: str,
    payload: HiringReadyRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    principal = get_request_principal(request) or {}

    try:
        hiring_record = _hiring_service.create_hiring_record(
            organization_id=organization_id,
            application_id=application_id,
            readiness_source=payload.readiness_source,
            waiver_reason=payload.waiver_reason,
        )
    except ValueError as error:
        _handle_service_error(error)

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="hiring",
        action="ready_for_hiring",
        entity_type="application",
        entity_id=str(application_id),
        status="success",
        details={
            "readiness_source": payload.readiness_source,
            "waiver_reason": payload.waiver_reason,
            "hiring_status": hiring_record.get("status"),
        },
    )

    return {
        "message": "Candidate is now Ready for Hiring.",
        "hiring_record": hiring_record,
    }


@router.post("/{application_id}/offer")
async def create_hiring_offer(
    application_id: str,
    payload: HiringOfferRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    principal = get_request_principal(request) or {}

    try:
        offer = _hiring_service.create_offer(
            organization_id=organization_id,
            application_id=application_id,
            offer_title=payload.offer_title,
            employment_type=payload.employment_type,
            salary_amount=payload.salary_amount,
            salary_currency=payload.salary_currency,
            start_date=(
                payload.start_date.isoformat()
                if payload.start_date
                else None
            ),
            offer_expiry_date=(
                payload.offer_expiry_date.isoformat()
                if payload.offer_expiry_date
                else None
            ),
            terms_and_conditions=payload.terms_and_conditions,
        )
    except ValueError as error:
        _handle_service_error(error)

    if offer is None:
        raise HTTPException(
            status_code=404,
            detail="Hiring record not found or candidate is not Ready for Hiring.",
        )

    try:
        NotificationService().send_notification(
            event_type="OFFER_CREATED",
            recipient="offers@talentbridgebd.com",
            subject_data={
                "job_title": payload.offer_title,
            },
        )
    except Exception as notification_error:
        print(
            f"[OFFER NOTIFICATION ERROR] {notification_error}"
        )

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="hiring",
        action="offer_create",
        entity_type="offer",
        entity_id=str(offer.get("id")),
        status="success",
        details={
            "application_id": str(application_id),
            "offer_title": offer.get("offer_title"),
            "status": offer.get("status"),
            "employment_type": offer.get("employment_type"),
            "salary_currency": offer.get("salary_currency"),
            "start_date": offer.get("start_date"),
            "offer_expiry_date": offer.get("offer_expiry_date"),
        },
    )

    return {
        "message": "Offer created successfully.",
        "offer": offer,
    }


@router.post("/{application_id}/offer/{offer_id}/send")
async def send_hiring_offer(
    application_id: str,
    offer_id: str,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    principal = get_request_principal(request) or {}

    offer = _hiring_service.send_offer(
        organization_id=organization_id,
        application_id=application_id,
        offer_id=offer_id,
    )

    if offer is None:
        raise HTTPException(
            status_code=409,
            detail="Offer could not be sent. It may no longer be a draft or may not belong to this organization.",
        )

    try:
        application = _hiring_service.get_hiring_application(
            organization_id,
            application_id,
        )

        if application and application.candidate_email:
            NotificationService().send_notification(
                event_type="OFFER_SENT",
                recipient=application.candidate_email,
                subject_data={
                    "offer_id": offer_id,
                },
            )

    except Exception as notification_error:
        print(
            f"[OFFER SENT NOTIFICATION ERROR] {notification_error}"
        )

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="hiring",
        action="offer_send",
        entity_type="offer",
        entity_id=str(offer.get("id")),
        status="success",
        details={
            "application_id": str(application_id),
            "status": offer.get("status"),
        },
    )

    return {
        "message": "Offer sent successfully.",
        "offer": offer,
    }


@router.put("/{application_id}/offer/{offer_id}")
async def update_hiring_offer(
    application_id: str,
    offer_id: str,
    payload: HiringOfferUpdateRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    principal = get_request_principal(request) or {}

    previous_offer = _hiring_service.get_offer(
        organization_id,
        application_id,
        offer_id,
    )

    if previous_offer is None:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    previous_status = previous_offer.get("status")

    try:
        offer = _hiring_service.update_offer(
            organization_id=organization_id,
            application_id=application_id,
            offer_id=offer_id,
            offer_title=payload.offer_title,
            employment_type=payload.employment_type,
            salary_amount=payload.salary_amount,
            salary_currency=payload.salary_currency,
            start_date=(
                payload.start_date.isoformat()
                if payload.start_date
                else None
            ),
            offer_expiry_date=(
                payload.offer_expiry_date.isoformat()
                if payload.offer_expiry_date
                else None
            ),
            terms_and_conditions=payload.terms_and_conditions,
            status=payload.status,
        )
    except ValueError as error:
        _handle_service_error(error)

    if offer is None:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="hiring",
        action="offer_update",
        entity_type="offer",
        entity_id=str(offer.get("id")),
        status="success",
        details={
            "application_id": str(application_id),
            "previous_status": previous_status,
            "new_status": offer.get("status"),
            "offer_title": offer.get("offer_title"),
        },
    )

    return {
        "message": "Offer updated successfully.",
        "offer": offer,
    }


class HiringHireRequest(BaseModel):
    offer_id: str


@router.post("/{application_id}/hire")
async def hire_candidate(
    application_id: str,
    payload: HiringHireRequest,
    organization_id: str,
    request: Request,
):
    _require_organization_access(
        request,
        organization_id,
    )

    principal = get_request_principal(request) or {}

    try:
        hiring_record = _hiring_service.hire(
            organization_id,
            application_id,
            payload.offer_id,
        )
    except ValueError as error:
        _handle_service_error(error)

    if hiring_record is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate could not be hired.",
        )

    _audit_log_repository.create_log(
        user_id=principal.get("id"),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=organization_id,
        event_type="hiring",
        action="hire",
        entity_type="application",
        entity_id=str(application_id),
        status="success",
        details={
            "offer_id": str(payload.offer_id),
            "previous_hiring_status": "offered",
            "new_hiring_status": hiring_record.get("status"),
            "application_status": "hired",
        },
    )

    return {
        "message": "Candidate marked as hired.",
        "hiring_record": hiring_record,
    }
