from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class VisaProcessing:
    id: str
    application_id: str

    visa_type: Optional[str] = None
    visa_number: Optional[str] = None
    application_number: Optional[str] = None

    submission_date: Optional[date] = None
    approval_date: Optional[date] = None
    expiry_date: Optional[date] = None

    status: str = "Pending"

    sponsor_name: Optional[str] = None
    sponsor_reference: Optional[str] = None
    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
