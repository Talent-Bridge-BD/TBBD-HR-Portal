from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class JobCompensation:
    id: str
    job_id: str
    salary_currency: Optional[str] = None
    basic_salary: Optional[Decimal] = None
    overtime_rate: Optional[Decimal] = None
    food_provided: bool = False
    accommodation_provided: bool = False
    transportation_provided: bool = False
    medical_coverage: bool = False
    air_ticket_provided: bool = False
    leave_entitlement: Optional[str] = None
    other_benefits: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
