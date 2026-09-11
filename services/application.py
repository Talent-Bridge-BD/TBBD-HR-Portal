from typing import Optional

from models.application import EmployerApplication
from repositories.application import ApplicationRepository


class ApplicationService:

    def __init__(self, repository: ApplicationRepository):
        self.repository = repository

    def list_applications(
        self,
        organization_id: str,
    ) -> list[EmployerApplication]:
        return self.repository.list_applications(
            organization_id,
        )

    def get_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> Optional[EmployerApplication]:
        return self.repository.get_application(
            organization_id,
            application_id,
        )

    def list_candidate_applications(
        self,
        candidate_id: str,
    ) -> list[EmployerApplication]:
        return self.repository.list_candidate_applications(
            candidate_id,
        )

    def create_application(
        self,
        candidate_id: str,
        job_id: str,
        cover_letter: Optional[str] = None,
    ) -> EmployerApplication:
        return self.repository.create_application(
            candidate_id,
            job_id,
            cover_letter,
        )
