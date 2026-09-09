from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class JobRequest:
    id: str
    organization_id: str
    requested_by: str
    title: str
    description: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    number_of_positions: Optional[int] = None
    status: str = "pending"
    requested_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
