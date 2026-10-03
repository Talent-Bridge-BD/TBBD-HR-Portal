from typing import Optional

from models.job_compensation import JobCompensation
from repositories.job_compensation import JobCompensationRepository


class JobCompensationService:
    def __init__(self, repository: JobCompensationRepository):
        self.repository = repository

    def get_by_job_id(
        self,
        job_id: str,
    ) -> Optional[JobCompensation]:
        return self.repository.get_by_job_id(job_id)

    def save(
        self,
        compensation: JobCompensation,
    ) -> JobCompensation:
        return self.repository.save(compensation)
