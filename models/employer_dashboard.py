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
    applied: int
    screening: int
    interview: int
    trade_test: int
    medical: int
    visa_processing: int
    ticketing: int
    onboarding: int
    deployment: int
    completed: int


@dataclass(frozen=True)
class EmployerDashboard:
    employer_name: str
    organization_name: Optional[str]
    stats: EmployerDashboardStats
    pipeline: EmployerPipeline
