from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EmployerInterview:
    id: str
    application_id: str
    candidate_id: str
    job_id: str
    candidate_first_name: str
    candidate_last_name: str
    candidate_email: str
    job_title: str
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    interview_type: Optional[str] = None
    location_or_link: Optional[str] = None
    interviewer_name: Optional[str] = None
    notes: Optional[str] = None
    status: str = "scheduled"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
