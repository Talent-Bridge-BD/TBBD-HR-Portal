from __future__ import annotations

from typing import Optional

from models.candidate_language import CandidateLanguage
from repositories.candidate_language import CandidateLanguageRepository


class CandidateLanguageService:

    def __init__(self, repository: CandidateLanguageRepository):
        self.repository = repository

    def list_languages(
        self,
        user_id: str,
    ) -> list[CandidateLanguage]:
        return self.repository.list_languages(user_id)

    def create_language(
        self,
        user_id: str,
        language_name: str,
        speaking_proficiency: Optional[str],
        reading_proficiency: Optional[str],
        writing_proficiency: Optional[str],
    ) -> CandidateLanguage:
        return self.repository.create_language(
            user_id,
            language_name,
            speaking_proficiency,
            reading_proficiency,
            writing_proficiency,
        )

    def update_language(
        self,
        user_id: str,
        language_id: str,
        language_name: str,
        speaking_proficiency: Optional[str],
        reading_proficiency: Optional[str],
        writing_proficiency: Optional[str],
    ) -> Optional[CandidateLanguage]:
        return self.repository.update_language(
            user_id,
            language_id,
            language_name,
            speaking_proficiency,
            reading_proficiency,
            writing_proficiency,
        )

    def delete_language(
        self,
        user_id: str,
        language_id: str,
    ) -> bool:
        return self.repository.delete_language(
            user_id,
            language_id,
        )
