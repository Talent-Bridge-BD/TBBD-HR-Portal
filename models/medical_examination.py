from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MedicalExamination:
    id: str
    application_id: str
    medical_center: Optional[str] = None
    examination_date: Optional[datetime] = None
    doctor_name: Optional[str] = None
    medical_type: Optional[str] = None
    status: str = "Scheduled"
    result: str = "Pending"
    report_notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
