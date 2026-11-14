from datetime import date

from repositories.candidate_education import SqlCandidateEducationRepository


class CandidateEducationService:
    def __init__(self, repository: SqlCandidateEducationRepository):
        self.repository = repository

    def list_education(self, candidate_id: str):
        return self.repository.list_education(candidate_id)

    def create_education(
        self,
        candidate_id: str,
        degree_qualification: str | None,
        institution: str | None,
        field_of_study: str | None,
        start_date: date | None,
        end_date: date | None,
        description: str | None,
    ):
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
        degree_qualification: str | None,
        institution: str | None,
        field_of_study: str | None,
        start_date: date | None,
        end_date: date | None,
        description: str | None,
    ):
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

    def delete_education(self, candidate_id: str, education_id: str) -> bool:
        return self.repository.delete_education(candidate_id, education_id)
