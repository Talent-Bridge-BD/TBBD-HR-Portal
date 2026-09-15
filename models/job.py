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
    requisition_number: Optional[str] = None
    employer_name: Optional[str] = None
    employer_country: Optional[str] = None
    employer_city: Optional[str] = None
    trade_skill_category: Optional[str] = None
    industry_sector: Optional[str] = None
    gender_requirement: Optional[str] = None
    minimum_age: Optional[int] = None
    maximum_age: Optional[int] = None
    contract_duration: Optional[str] = None
    work_location: Optional[str] = None
    project_name: Optional[str] = None
    published_at: Optional[datetime] = None
    closing_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
