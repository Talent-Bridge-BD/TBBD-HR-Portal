from models.candidate_education import CandidateEducation
from repositories.candidate_education import CandidateEducationRepository


class CandidateEducationService:
    def __init__(self, repository: CandidateEducationRepository):
        self.repository = repository

    def list_education(
        self,
        candidate_id: str,
    ) -> list[CandidateEducation]:
        return self.repository.list_education(candidate_id)

    def get_education(
        self,
        candidate_id: str,
        education_id: str,
    ) -> CandidateEducation | None:
        return self.repository.get_education(
            candidate_id,
            education_id,
        )

    def create_education(
        self,
        candidate_id: str,
        degree_qualification: str,
        institution: str,
        field_of_study: str | None,
        start_date,
        end_date,
        description: str | None,
    ) -> CandidateEducation:
        return self.repository.create_education(
            candidate_id,
            degree_qualification,
            institution,
            field_of_study,
            start_date,
            end_date,
            description,
        )

    def update_education(
        self,
        candidate_id: str,
        education_id: str,
        degree_qualification: str,
        institution: str,
        field_of_study: str | None,
        start_date,
        end_date,
        description: str | None,
    ) -> CandidateEducation | None:
        return self.repository.update_education(
            candidate_id,
            education_id,
            degree_qualification,
            institution,
            field_of_study,
            start_date,
            end_date,
            description,
        )

    def delete_education(
        self,
        candidate_id: str,
        education_id: str,
    ) -> bool:
        return self.repository.delete_education(
            candidate_id,
            education_id,
        )
