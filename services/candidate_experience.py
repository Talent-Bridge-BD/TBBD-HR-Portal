from models.candidate_experience import CandidateExperience
from repositories.candidate_experience import CandidateExperienceRepository


class CandidateExperienceService:
    def __init__(self, repository: CandidateExperienceRepository):
        self.repository = repository

    def list_experience(
        self,
        candidate_id: str,
    ) -> list[CandidateExperience]:
        return self.repository.list_experience(candidate_id)

    def get_experience(
        self,
        candidate_id: str,
        experience_id: str,
    ) -> CandidateExperience | None:
        return self.repository.get_experience(
            candidate_id,
            experience_id,
        )

    def create_experience(
        self,
        candidate_id: str,
        job_title: str,
        company: str,
        location: str | None,
        employment_type: str | None,
        start_date,
        end_date,
        currently_working: bool,
        description: str | None,
    ) -> CandidateExperience:
        return self.repository.create_experience(
            candidate_id,
            job_title,
            company,
            location,
            employment_type,
            start_date,
            end_date,
            currently_working,
            description,
        )

    def update_experience(
        self,
        candidate_id: str,
        experience_id: str,
        job_title: str,
        company: str,
        location: str | None,
        employment_type: str | None,
        start_date,
        end_date,
        currently_working: bool,
        description: str | None,
    ) -> CandidateExperience | None:
        return self.repository.update_experience(
            candidate_id,
            experience_id,
            job_title,
            company,
            location,
            employment_type,
            start_date,
            end_date,
            currently_working,
            description,
        )

    def delete_experience(
        self,
        candidate_id: str,
        experience_id: str,
    ) -> bool:
        return self.repository.delete_experience(
            candidate_id,
            experience_id,
        )
