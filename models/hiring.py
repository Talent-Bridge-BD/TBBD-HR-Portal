from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class HiringApplication:
    id: str
    candidate_id: str
    job_id: str
    candidate_first_name: str
    candidate_last_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None
    job_title: str = ""
    status: str = "submitted"
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
