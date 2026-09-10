from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.candidate_skill import CandidateSkill


class CandidateSkillRepository(ABC):

    @abstractmethod
    def list_skills(self, candidate_id: str) -> list[CandidateSkill]:
        raise NotImplementedError

    @abstractmethod
    def get_skill(
        self,
        candidate_id: str,
        skill_id: str,
    ) -> Optional[CandidateSkill]:
        raise NotImplementedError

    @abstractmethod
    def create_skill(
        self,
        candidate_id: str,
        skill_name: str,
        skill_category: str | None,
        proficiency: str | None,
    ) -> CandidateSkill:
        raise NotImplementedError

    @abstractmethod
    def update_skill(
        self,
        candidate_id: str,
        skill_id: str,
        skill_name: str,
        skill_category: str | None,
        proficiency: str | None,
    ) -> Optional[CandidateSkill]:
        raise NotImplementedError

    @abstractmethod
    def delete_skill(
        self,
        candidate_id: str,
        skill_id: str,
    ) -> bool:
        raise NotImplementedError


class SqlCandidateSkillRepository(CandidateSkillRepository):

    SERVER = "tbbd-sql-sea.database.windows.net"
    DATABASE = "tbbd-hr-db"
    DRIVER = "{ODBC Driver 18 for SQL Server}"

    def _get_connection(self):
        credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=False
        )
        token = credential.get_token(
            "https://database.windows.net/.default"
        )

        token_bytes = token.token.encode("utf-16-le")
        token_struct = (
            len(token_bytes).to_bytes(4, "little")
            + token_bytes
        )

        return pyodbc.connect(
            (
                f"DRIVER={self.DRIVER};"
                f"SERVER={self.SERVER};"
                f"DATABASE={self.DATABASE};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
            ),
            attrs_before={1256: token_struct},
        )

    @staticmethod
    def _map_row(row) -> CandidateSkill:
        return CandidateSkill(
            id=str(row[0]),
            candidate_id=str(row[1]),
            skill_name=row[2],
            skill_category=row[3],
            proficiency=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def list_skills(
        self,
        candidate_id: str,
    ) -> list[CandidateSkill]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    s.id,
                    s.candidate_id,
                    s.skill_name,
                    s.skill_category,
                    s.proficiency,
                    s.created_at,
                    s.updated_at
                FROM dbo.candidate_skills AS s
                INNER JOIN dbo.candidates AS c
                    ON c.id = s.candidate_id
                WHERE c.entra_object_id = ?
                ORDER BY s.skill_name ASC;
                """,
                candidate_id,
            )

            return [
                self._map_row(row)
                for row in cursor.fetchall()
            ]

    def get_skill(
        self,
        candidate_id: str,
        skill_id: str,
    ) -> Optional[CandidateSkill]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    s.id,
                    s.candidate_id,
                    s.skill_name,
                    s.skill_category,
                    s.proficiency,
                    s.created_at,
                    s.updated_at
                FROM dbo.candidate_skills AS s
                INNER JOIN dbo.candidates AS c
                    ON c.id = s.candidate_id
                WHERE s.id = ?
                  AND c.entra_object_id = ?;
                """,
                skill_id,
                candidate_id,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._map_row(row)

    def create_skill(
        self,
        candidate_id: str,
        skill_name: str,
        skill_category: str | None,
        proficiency: str | None,
    ) -> CandidateSkill:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.candidate_skills (
                    candidate_id,
                    skill_name,
                    skill_category,
                    proficiency
                )
                OUTPUT
                    INSERTED.id,
                    INSERTED.candidate_id,
                    INSERTED.skill_name,
                    INSERTED.skill_category,
                    INSERTED.proficiency,
                    INSERTED.created_at,
                    INSERTED.updated_at
                SELECT
                    c.id,
                    ?,
                    ?,
                    ?
                FROM dbo.candidates AS c
                WHERE c.entra_object_id = ?;
                """,
                skill_name,
                skill_category,
                proficiency,
                candidate_id,
            )

            row = cursor.fetchone()

            if row is None:
                raise ValueError(
                    "Candidate profile not found"
                )

            conn.commit()

            return self._map_row(row)

    def update_skill(
        self,
        candidate_id: str,
        skill_id: str,
        skill_name: str,
        skill_category: str | None,
        proficiency: str | None,
    ) -> Optional[CandidateSkill]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE s
                SET
                    skill_name = ?,
                    skill_category = ?,
                    proficiency = ?,
                    updated_at = SYSUTCDATETIME()
                OUTPUT
                    INSERTED.id,
                    INSERTED.candidate_id,
                    INSERTED.skill_name,
                    INSERTED.skill_category,
                    INSERTED.proficiency,
                    INSERTED.created_at,
                    INSERTED.updated_at
                FROM dbo.candidate_skills AS s
                INNER JOIN dbo.candidates AS c
                    ON c.id = s.candidate_id
                WHERE s.id = ?
                  AND c.entra_object_id = ?;
                """,
                skill_name,
                skill_category,
                proficiency,
                skill_id,
                candidate_id,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            conn.commit()

            return self._map_row(row)

    def delete_skill(
        self,
        candidate_id: str,
        skill_id: str,
    ) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE s
                FROM dbo.candidate_skills AS s
                INNER JOIN dbo.candidates AS c
                    ON c.id = s.candidate_id
                WHERE s.id = ?
                  AND c.entra_object_id = ?;
                """,
                skill_id,
                candidate_id,
            )

            deleted = cursor.rowcount > 0

            conn.commit()

            return deleted
