from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class CandidateEducation:
    id: str
    candidate_id: str
    degree_qualification: str | None
    institution: str | None
    field_of_study: str | None
    start_date: date | None
    end_date: date | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    passing_year: int | None
    result_gpa: str | None