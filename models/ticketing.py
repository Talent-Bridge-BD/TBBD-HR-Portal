from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Ticketing:
    id: str
    application_id: str

    airline_name: Optional[str] = None
    flight_number: Optional[str] = None
    booking_reference: Optional[str] = None
    ticket_number: Optional[str] = None

    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None

    departure_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None

    status: str = "Pending"

    ticket_document_reference: Optional[str] = None
    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
