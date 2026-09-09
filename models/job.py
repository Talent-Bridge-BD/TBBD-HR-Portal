from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Job:
    id: str
    organization_id: str
    title: str
    description: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    status: str = "draft"
    number_of_positions: Optional[int] = None
    published_at: Optional[datetime] = None
    closing_at: Optional[datetime] = None
    job_reference: Optional[str] = None
    department: Optional[str] = None
    job_category: Optional[str] = None
    workplace_type: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    salary_compensation: Optional[str] = None
    application_instructions: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
