from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class CandidateExperience:
    id: str
    candidate_id: str
    job_title: str
    company: str
    location: Optional[str]
    employment_type: Optional[str]
    start_date: date
    end_date: Optional[date]
    currently_working: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
