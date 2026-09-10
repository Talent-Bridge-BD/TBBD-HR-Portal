from models.candidate_preferences import CandidatePreferences
from repositories.candidate_preferences import CandidatePreferencesRepository


class CandidatePreferencesService:

    def __init__(self, repository: CandidatePreferencesRepository):
        self.repository = repository

    def get_preferences(
        self,
        candidate_id: str,
    ) -> CandidatePreferences | None:
        return self.repository.get_preferences(candidate_id)

    def save_preferences(
        self,
        candidate_id: str,
        preferred_job_title: str | None,
        preferred_location: str | None,
        preferred_employment_type: str | None,
        work_arrangement: str | None,
        expected_salary: float | None,
        currency: str | None,
        availability_notice_period: str | None,
        open_to_relocation: bool | None,
        available_for_recruitment: bool,
        preferred_contact_method: str | None,
    ) -> CandidatePreferences:
        return self.repository.save_preferences(
            candidate_id,
            preferred_job_title,
            preferred_location,
            preferred_employment_type,
            work_arrangement,
            expected_salary,
            currency,
            availability_notice_period,
            open_to_relocation,
            available_for_recruitment,
            preferred_contact_method,
        )
