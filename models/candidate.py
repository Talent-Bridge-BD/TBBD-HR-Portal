from dataclasses import dataclass
from typing import Optional


@dataclass
class CandidateProfile:
    user_id: str

    # Personal information
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""

    # Professional profile
    professional_title: str = ""
    summary: str = ""
    career_level: str = ""
    years_experience: Optional[float] = None

    # Passport / international mobility
    passport_number: str = ""
    passport_country: str = ""
    passport_expiry_date: Optional[str] = None
    passport_status: str = ""
    international_travel_readiness: str = ""

    workflow_status: str = "Applied"

    # Existing document reference
    resume_document_id: Optional[str] = None

    # Related candidate data
    skills: list[dict] | None = None
    preferences: dict | None = None
    experience: list[dict] | None = None
    education: list[dict] | None = None
    certifications: list[dict] | None = None
    languages: list[dict] | None = None
