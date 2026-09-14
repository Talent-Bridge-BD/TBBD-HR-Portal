from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CandidateLanguage:
    id: str
    candidate_id: str
    language_name: str
    speaking_proficiency: Optional[str] = None
    reading_proficiency: Optional[str] = None
    writing_proficiency: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
