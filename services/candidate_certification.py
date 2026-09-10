from datetime import date
from typing import List, Optional

from models.candidate_certification import CandidateCertification
from repositories.candidate_certification import (
    CandidateCertificationRepository,
)


class CandidateCertificationService:
    def __init__(self, repository: CandidateCertificationRepository):
        self.repository = repository

    def list_certifications(
        self,
        candidate_id: str,
    ) -> List[CandidateCertification]:
        return self.repository.list_certifications(candidate_id)

    def get_certification(
        self,
        candidate_id: str,
        certification_id: str,
    ) -> Optional[CandidateCertification]:
        return self.repository.get_certification(
            candidate_id,
            certification_id,
        )

    def create_certification(
        self,
        candidate_id: str,
        certification_name: str,
        issuing_organization: str,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        credential_id: Optional[str],
    ) -> Optional[CandidateCertification]:
        return self.repository.create_certification(
            candidate_id,
            certification_name,
            issuing_organization,
            issue_date,
            expiry_date,
            credential_id,
        )

    def update_certification(
        self,
        candidate_id: str,
        certification_id: str,
        certification_name: str,
        issuing_organization: str,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        credential_id: Optional[str],
    ) -> Optional[CandidateCertification]:
        return self.repository.update_certification(
            candidate_id,
            certification_id,
            certification_name,
            issuing_organization,
            issue_date,
            expiry_date,
            credential_id,
        )

    def delete_certification(
        self,
        candidate_id: str,
        certification_id: str,
    ) -> bool:
        return self.repository.delete_certification(
            candidate_id,
            certification_id,
        )
