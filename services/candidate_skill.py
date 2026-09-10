from models.candidate_skill import CandidateSkill
from repositories.candidate_skill import CandidateSkillRepository


class CandidateSkillService:
    def __init__(self, repository: CandidateSkillRepository):
        self.repository = repository

    def list_skills(
        self,
        candidate_id: str,
    ) -> list[CandidateSkill]:
        return self.repository.list_skills(candidate_id)

    def get_skill(
        self,
        candidate_id: str,
        skill_id: str,
    ) -> CandidateSkill | None:
        return self.repository.get_skill(
            candidate_id,
            skill_id,
        )

    def create_skill(
        self,
        candidate_id: str,
        skill_name: str,
        skill_category: str | None,
        proficiency: str | None,
    ) -> CandidateSkill:
        return self.repository.create_skill(
            candidate_id,
            skill_name,
            skill_category,
            proficiency,
        )

    def update_skill(
        self,
        candidate_id: str,
        skill_id: str,
        skill_name: str,
        skill_category: str | None,
        proficiency: str | None,
    ) -> CandidateSkill | None:
        return self.repository.update_skill(
            candidate_id,
            skill_id,
            skill_name,
            skill_category,
            proficiency,
        )

    def delete_skill(
        self,
        candidate_id: str,
        skill_id: str,
    ) -> bool:
        return self.repository.delete_skill(
            candidate_id,
            skill_id,
        )
