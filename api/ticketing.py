from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from repositories.ticketing import SqlTicketingRepository
from services.ticketing import TicketingService


router = APIRouter(
    prefix="/api/ticketing",
    tags=["ticketing"],
)

_repository = SqlTicketingRepository()
_service = TicketingService(_repository)


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
    application_id: str = Query(...),
):
    return _service.list_by_application(application_id)


@router.post("")
def create_ticketing(
    request: TicketingCreateRequest,
):
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
):
    ticketing = _service.get(ticketing_id)

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
):
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
