from typing import Optional

from models.hiring import HiringApplication
from repositories.hiring import HiringRepository


class HiringService:

    def __init__(self, repository: HiringRepository):
        self.repository = repository

    def list_hiring_applications(
        self,
        organization_id: str,
    ) -> list[HiringApplication]:
        return self.repository.list_hiring_applications(
            organization_id,
        )

    def get_hiring_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> Optional[HiringApplication]:
        return self.repository.get_hiring_application(
            organization_id,
            application_id,
        )
