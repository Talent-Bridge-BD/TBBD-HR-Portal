from __future__ import annotations

from datetime import date
from typing import Optional

from models.candidate_experience import CandidateExperience
from repositories.candidate_experience import CandidateExperienceRepository


class CandidateExperienceService:

    def __init__(self, repository: CandidateExperienceRepository):
        self.repository = repository

    def list_experience(self, user_id: str) -> list[CandidateExperience]:
        return self.repository.list_experience(user_id)

    def create_experience(
        self,
        user_id: str,
        job_title: str,
        company: str,
        location: Optional[str],
        employment_type: Optional[str],
        start_date: date,
        end_date: Optional[date],
        currently_working: bool,
        description: Optional[str],
    ) -> CandidateExperience:
        return self.repository.create_experience(
            user_id,
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
        user_id: str,
        experience_id: str,
        job_title: str,
        company: str,
        location: Optional[str],
        employment_type: Optional[str],
        start_date: date,
        end_date: Optional[date],
        currently_working: bool,
        description: Optional[str],
    ) -> Optional[CandidateExperience]:
        return self.repository.update_experience(
            user_id,
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
        user_id: str,
        experience_id: str,
    ) -> bool:
        return self.repository.delete_experience(
            user_id,
            experience_id,
        )
