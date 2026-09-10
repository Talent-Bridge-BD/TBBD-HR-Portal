from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class EmployerOffer:
    id: str
    application_id: str
    candidate_id: str
    job_id: str
    candidate_first_name: str
    candidate_last_name: str
    candidate_email: str
    job_title: str
    offer_date: datetime
    expiry_date: Optional[datetime] = None
    start_date: Optional[date] = None
    employment_type: Optional[str] = None
    salary_compensation: Optional[str] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
