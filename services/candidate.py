from typing import Optional

from models.candidate import CandidateProfile
from repositories.candidate import CandidateRepository


class CandidateService:
    def __init__(self, repository: CandidateRepository):
        self.repository = repository

    def get_profile(self, user_id: str) -> Optional[CandidateProfile]:
        return self.repository.get_profile(user_id)

    def save_profile(self, profile: CandidateProfile) -> CandidateProfile:
        return self.repository.save_profile(profile)

    def get_candidate_id(self, user_id: str) -> Optional[str]:
        return self.repository.get_candidate_id(user_id)
