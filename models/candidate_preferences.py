from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CandidatePreferences:
    id: str
    candidate_id: str
    preferred_job_title: Optional[str] = None
    preferred_location: Optional[str] = None
    preferred_employment_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    expected_salary: Optional[float] = None
    currency: Optional[str] = None
    availability_notice_period: Optional[str] = None
    open_to_relocation: Optional[bool] = None
    available_for_recruitment: bool = True
    preferred_contact_method: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
