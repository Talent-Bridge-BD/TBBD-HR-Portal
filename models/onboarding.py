from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class OnboardingRecord:
    id: str
    application_id: str
    candidate_id: str
    job_id: str
    candidate_first_name: str
    candidate_last_name: str
    candidate_email: str
    job_title: str
    status: str = "pending"
    planned_start_date: Optional[date] = None
    employment_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
