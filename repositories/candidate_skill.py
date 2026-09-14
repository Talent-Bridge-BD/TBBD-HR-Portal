from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.candidate_skill import CandidateSkill


class CandidateSkillRepository(ABC):

    @abstractmethod
    def list_skills(self, user_id: str) -> list[CandidateSkill]:
        raise NotImplementedError

    @abstractmethod
    def create_skill(
        self,
        user_id: str,
        skill_name: str,
        skill_category: Optional[str],
        proficiency: Optional[str],
    ) -> CandidateSkill:
        raise NotImplementedError

    @abstractmethod
    def update_skill(
        self,
        user_id: str,
        skill_id: str,
        skill_name: str,
        skill_category: Optional[str],
        proficiency: Optional[str],
    ) -> Optional[CandidateSkill]:
        raise NotImplementedError

    @abstractmethod
    def delete_skill(
        self,
        user_id: str,
        skill_id: str,
    ) -> bool:
        raise NotImplementedError


class SqlCandidateSkillRepository(CandidateSkillRepository):
    """
    Azure SQL implementation using Microsoft Entra authentication.

    Candidate ownership is enforced through dbo.candidates.entra_object_id
    on every read, update, and delete operation.
    """

    SQL_ACCESS_TOKEN_ATTRIBUTE = 1256
    SQL_SCOPE = "https://database.windows.net/.default"

    def __init__(
        self,
        server: str | None = None,
        database: str | None = None,
    ):
        self.server = server or os.environ.get(
            "SQL_SERVER",
            "tbbd-sql-sea.database.windows.net",
        )
        self.database = database or os.environ.get(
            "SQL_DATABASE",
            "tbbd-hr-db",
        )
        self.credential = DefaultAzureCredential()

    def _connection(self) -> pyodbc.Connection:
        token = self.credential.get_token(self.SQL_SCOPE).token
        token_bytes = token.encode("utf-16-le")
        token_struct = struct.pack(
            f"<I{len(token_bytes)}s",
            len(token_bytes),
            token_bytes,
        )

        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self.server},1433;"
            f"DATABASE={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        return pyodbc.connect(
            connection_string,
            attrs_before={
                self.SQL_ACCESS_TOKEN_ATTRIBUTE: token_struct,
            },
        )

    @staticmethod
    def _map_row(row) -> CandidateSkill:
        return CandidateSkill(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            skill_name=row.skill_name,
            skill_category=row.skill_category,
            proficiency=row.proficiency,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_skills(self, user_id: str) -> list[CandidateSkill]:
        sql = """
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
        ORDER BY
            s.skill_name ASC,
            s.created_at ASC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, user_id)
            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def create_skill(
        self,
        user_id: str,
        skill_name: str,
        skill_category: Optional[str],
        proficiency: Optional[str],
    ) -> CandidateSkill:
        sql = """
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
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                skill_name,
                skill_category,
                proficiency,
                user_id,
            )
            row = cursor.fetchone()

            if row is None:
                raise ValueError("Candidate profile was not found.")

        connection.commit()
        return self._map_row(row)

    def update_skill(
        self,
        user_id: str,
        skill_id: str,
        skill_name: str,
        skill_category: Optional[str],
        proficiency: Optional[str],
    ) -> Optional[CandidateSkill]:
        sql = """
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
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                skill_name,
                skill_category,
                proficiency,
                skill_id,
                user_id,
            )
            row = cursor.fetchone()

            if row is None:
                return None

            connection.commit()

        return self._map_row(row)

    def delete_skill(
        self,
        user_id: str,
        skill_id: str,
    ) -> bool:
        sql = """
        DELETE s
        FROM dbo.candidate_skills AS s
        INNER JOIN dbo.candidates AS c
            ON c.id = s.candidate_id
        WHERE s.id = ?
          AND c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                skill_id,
                user_id,
            )
            deleted = cursor.rowcount > 0
            connection.commit()

        return deleted
