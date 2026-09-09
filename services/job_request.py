from typing import Optional

from models.job_request import JobRequest
from repositories.job_request import JobRequestRepository


class JobRequestService:
    def __init__(self, repository: JobRequestRepository):
        self.repository = repository

    def list_requests(
        self,
        organization_id: str,
    ) -> list[JobRequest]:
        return self.repository.list_requests(organization_id)

    def get_request(
        self,
        organization_id: str,
        request_id: str,
    ) -> Optional[JobRequest]:
        return self.repository.get_request(
            organization_id,
            request_id,
        )

    def save_request(
        self,
        request: JobRequest,
    ) -> JobRequest:
        return self.repository.save_request(request)
