from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from repositories.application import SqlApplicationRepository
from repositories.organization import SqlOrganizationRepository
from repositories.ticketing import SqlTicketingRepository
from services.authorization import (
    build_authorization_context_from_principal,
    has_any_role,
    is_global_administrator,
)
from services.local_auth import get_request_principal
from services.ticketing import TicketingService


router = APIRouter(
    prefix="/api/ticketing",
    tags=["ticketing"],
)

_repository = SqlTicketingRepository()
_service = TicketingService(_repository)
_application_repository = SqlApplicationRepository()
_organization_repository = SqlOrganizationRepository()


def _get_authorization_context(request: Request):
    principal = get_request_principal(request)

    if not principal or not principal.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    role_context = build_authorization_context_from_principal(
        principal,
        [],
    )

    allowed_roles = {
        "Employer Manager",
        "HR Manager",
        "Administrator",
    }

    if not has_any_role(role_context, allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Recruitment management role is required",
        )

    memberships = _organization_repository.get_active_memberships(
        principal["id"],
    )

    return build_authorization_context_from_principal(
        principal,
        memberships,
    )


def _require_application_access(
    request: Request,
    application_id: str,
):
    context = _get_authorization_context(request)

    if is_global_administrator(context):
        application = _application_repository.get_application_by_id(
            application_id,
        )

        if application is None:
            raise HTTPException(
                status_code=404,
                detail="Application not found",
            )

        return context, application

    for organization_id in context.organization_ids:
        application = _application_repository.get_application(
            organization_id,
            application_id,
        )

        if application is not None:
            return context, application

    raise HTTPException(
        status_code=403,
        detail="You do not have access to this application",
    )


class TicketingCreateRequest(BaseModel):
    application_id: str

    airline_name: Optional[str] = None
    flight_number: Optional[str] = None
    booking_reference: Optional[str] = None
    ticket_number: Optional[str] = None

    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None

    departure_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None


class TicketingUpdateRequest(BaseModel):
    airline_name: Optional[str] = None
    flight_number: Optional[str] = None
    booking_reference: Optional[str] = None
    ticket_number: Optional[str] = None

    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None

    departure_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None

    status: str

    ticket_document_reference: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
def list_ticketing(
    request: Request,
    application_id: str = Query(...),
):
    _require_application_access(request, application_id)
    return _service.list_by_application(application_id)


@router.post("")
def create_ticketing(
    request: TicketingCreateRequest,
    http_request: Request,
):
    _require_application_access(http_request, request.application_id)

    try:
        return _service.create(
            application_id=request.application_id,
            airline_name=request.airline_name,
            flight_number=request.flight_number,
            booking_reference=request.booking_reference,
            ticket_number=request.ticket_number,
            departure_airport=request.departure_airport,
            arrival_airport=request.arrival_airport,
            departure_datetime=request.departure_datetime,
            arrival_datetime=request.arrival_datetime,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{ticketing_id}")
def get_ticketing(
    ticketing_id: str,
    request: Request,
):
    ticketing = _service.get(ticketing_id)

    if ticketing is not None:
        _require_application_access(request, ticketing.application_id)

    if ticketing is None:
        raise HTTPException(
            status_code=404,
            detail="Ticketing record not found",
        )

    return ticketing


@router.put("/{ticketing_id}")
def update_ticketing(
    ticketing_id: str,
    request: TicketingUpdateRequest,
    http_request: Request,
):
    ticketing = _service.get(ticketing_id)

    if ticketing is None:
        raise HTTPException(
            status_code=404,
            detail="Ticketing record not found",
        )

    _require_application_access(http_request, ticketing.application_id)

    try:
        return _service.update(
            ticketing_id=ticketing_id,
            airline_name=request.airline_name,
            flight_number=request.flight_number,
            booking_reference=request.booking_reference,
            ticket_number=request.ticket_number,
            departure_airport=request.departure_airport,
            arrival_airport=request.arrival_airport,
            departure_datetime=request.departure_datetime,
            arrival_datetime=request.arrival_datetime,
            status=request.status,
            ticket_document_reference=request.ticket_document_reference,
            notes=request.notes,
        )
    except ValueError as exc:
        if str(exc) == "Ticketing record not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
