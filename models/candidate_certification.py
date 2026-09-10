from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class CandidateCertification:
    id: str
    candidate_id: str
    certification_name: str
    issuing_organization: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
