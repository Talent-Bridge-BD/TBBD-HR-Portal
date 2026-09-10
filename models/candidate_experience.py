from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class CandidateExperience:
    id: str
    candidate_id: str
    job_title: str
    company: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: date | None = None
    end_date: date | None = None
    currently_working: bool = False
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
