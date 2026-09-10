from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CandidateSkill:
    id: str
    candidate_id: str
    skill_name: str
    skill_category: Optional[str] = None
    proficiency: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
