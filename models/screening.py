from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ScreeningAssessment:
    id: str
    application_id: str

    basic_eligibility: Optional[str] = None
    relevant_experience: Optional[str] = None
    education: Optional[str] = None
    communication: Optional[str] = None
    availability: Optional[str] = None

    screening_notes: Optional[str] = None
    recommendation: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
