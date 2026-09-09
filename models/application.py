from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EmployerApplication:
    id: str
    candidate_id: str
    job_id: str
    candidate_first_name: str
    candidate_last_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None
    job_title: str = ""
    status: str = "new"
    cover_letter: Optional[str] = None
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
