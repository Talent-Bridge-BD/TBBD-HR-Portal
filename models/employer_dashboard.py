from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EmployerDashboardStats:
    active_jobs: int
    new_applications: int
    candidates_pipeline: int
    interviews_upcoming: int


@dataclass(frozen=True)
class EmployerPipeline:
    new: int
    screening: int
    shortlisted: int
    interview: int
    offer: int
    hired: int


@dataclass(frozen=True)
class EmployerDashboard:
    employer_name: str
    organization_name: Optional[str]
    stats: EmployerDashboardStats
    pipeline: EmployerPipeline
