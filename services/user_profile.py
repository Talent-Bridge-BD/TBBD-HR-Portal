from typing import Optional

from models.user_profile import UserProfile
from repositories.user_profile import UserProfileRepository


class UserProfileService:

    def __init__(self, repository: UserProfileRepository):
        self.repository = repository

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        return self.repository.get_profile(user_id)

    def save_profile(self, profile: UserProfile) -> UserProfile:
        return self.repository.save_profile(profile)
