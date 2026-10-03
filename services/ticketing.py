from datetime import datetime
from typing import Optional

from models.ticketing import Ticketing
from repositories.ticketing import TicketingRepository


class TicketingService:

    ALLOWED_STATUSES = {
        "Pending",
        "Booked",
        "Issued",
        "Completed",
        "Cancelled",
    }

    def __init__(self, repository: TicketingRepository):
        self.repository = repository

    def list_by_application(
        self,
        application_id: str,
    ) -> list[Ticketing]:
        return self.repository.list_by_application(application_id)

    def create(
        self,
        application_id: str,
        airline_name: Optional[str] = None,
        flight_number: Optional[str] = None,
        booking_reference: Optional[str] = None,
        ticket_number: Optional[str] = None,
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        departure_datetime: Optional[datetime] = None,
        arrival_datetime: Optional[datetime] = None,
    ) -> Ticketing:

        return self.repository.create(
            application_id=application_id,
            airline_name=airline_name,
            flight_number=flight_number,
            booking_reference=booking_reference,
            ticket_number=ticket_number,
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_datetime=departure_datetime,
            arrival_datetime=arrival_datetime,
        )

    def get(
        self,
        ticketing_id: str,
    ) -> Ticketing | None:
        return self.repository.get(ticketing_id)

    def update(
        self,
        ticketing_id: str,
        airline_name: Optional[str],
        flight_number: Optional[str],
        booking_reference: Optional[str],
        ticket_number: Optional[str],
        departure_airport: Optional[str],
        arrival_airport: Optional[str],
        departure_datetime: Optional[datetime],
        arrival_datetime: Optional[datetime],
        status: str,
        ticket_document_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Ticketing:

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid ticketing status: {status}"
            )

        return self.repository.update(
            ticketing_id=ticketing_id,
            airline_name=airline_name,
            flight_number=flight_number,
            booking_reference=booking_reference,
            ticket_number=ticket_number,
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_datetime=departure_datetime,
            arrival_datetime=arrival_datetime,
            status=status,
            ticket_document_reference=ticket_document_reference,
            notes=notes,
        )
