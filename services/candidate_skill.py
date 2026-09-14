from __future__ import annotations

from typing import Optional

from models.candidate_skill import CandidateSkill
from repositories.candidate_skill import CandidateSkillRepository


class CandidateSkillService:
    def __init__(self, repository: CandidateSkillRepository):
        self.repository = repository

    def list_skills(self, user_id: str) -> list[CandidateSkill]:
        return self.repository.list_skills(user_id)

    def create_skill(
        self,
        user_id: str,
        skill_name: str,
        skill_category: Optional[str],
        proficiency: Optional[str],
    ) -> CandidateSkill:
        return self.repository.create_skill(
            user_id,
            skill_name,
            skill_category,
            proficiency,
        )

    def update_skill(
        self,
        user_id: str,
        skill_id: str,
        skill_name: str,
        skill_category: Optional[str],
        proficiency: Optional[str],
    ) -> Optional[CandidateSkill]:
        return self.repository.update_skill(
            user_id,
            skill_id,
            skill_name,
            skill_category,
            proficiency,
        )

    def delete_skill(
        self,
        user_id: str,
        skill_id: str,
    ) -> bool:
        return self.repository.delete_skill(
            user_id,
            skill_id,
        )
