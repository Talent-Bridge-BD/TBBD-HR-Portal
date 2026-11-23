from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Onboarding:
    id: str
    application_id: str

    employer_name: Optional[str] = None
    job_title: Optional[str] = None
    joining_date: Optional[date] = None

    status: str = "Pending"

    contract_signed: bool = False
    documents_verified: bool = False
    orientation_completed: bool = False
    accommodation_arranged: bool = False
    transport_arranged: bool = False

    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
