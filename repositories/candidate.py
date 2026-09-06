from abc import ABC, abstractmethod
from typing import Optional

from models.candidate import CandidateProfile


class CandidateRepository(ABC):
    @abstractmethod
    def get_profile(self, user_id: str) -> Optional[CandidateProfile]:
        raise NotImplementedError

    @abstractmethod
    def save_profile(self, profile: CandidateProfile) -> CandidateProfile:
        raise NotImplementedError


class InMemoryCandidateRepository(CandidateRepository):
    def __init__(self):
        self._profiles: dict[str, CandidateProfile] = {}

    def get_profile(self, user_id: str) -> Optional[CandidateProfile]:
        return self._profiles.get(user_id)

    def save_profile(self, profile: CandidateProfile) -> CandidateProfile:
        self._profiles[profile.user_id] = profile
        return profile
