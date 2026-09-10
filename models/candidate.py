from dataclasses import dataclass
from typing import Optional


@dataclass
class CandidateProfile:
    user_id: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    professional_title: str = ""
    summary: str = ""
    location: str = ""
    country: str = ""
    years_experience: Optional[float] = None
    current_company: str = ""
    resume_document_id: Optional[str] = None
