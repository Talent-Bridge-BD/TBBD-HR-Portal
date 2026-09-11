from typing import Optional

from models.job import Job
from repositories.job import JobRepository


class JobService:

    def __init__(self, repository: JobRepository):
        self.repository = repository

    def list_jobs(self, organization_id: str) -> list[Job]:
        return self.repository.list_jobs(organization_id)

    def list_published_jobs(self) -> list[Job]:
        return self.repository.list_published_jobs()

    def get_published_job(self, job_id: str) -> Optional[Job]:
        return self.repository.get_published_job(job_id)

    def get_job(
        self,
        organization_id: str,
        job_id: str,
    ) -> Optional[Job]:
        return self.repository.get_job(
            organization_id,
            job_id,
        )

    def save_job(self, job: Job) -> Job:
        return self.repository.save_job(job)
