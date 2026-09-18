from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import AzureCliCredential

from models.candidate_language import CandidateLanguage


class CandidateLanguageRepository(ABC):

    @abstractmethod
    def list_languages(self, user_id: str) -> list[CandidateLanguage]:
        raise NotImplementedError

    @abstractmethod
    def create_language(
        self,
        user_id: str,
        language_name: str,
        speaking_proficiency: Optional[str],
        reading_proficiency: Optional[str],
        writing_proficiency: Optional[str],
    ) -> CandidateLanguage:
        raise NotImplementedError

    @abstractmethod
    def update_language(
        self,
        user_id: str,
        language_id: str,
        language_name: str,
        speaking_proficiency: Optional[str],
        reading_proficiency: Optional[str],
        writing_proficiency: Optional[str],
    ) -> Optional[CandidateLanguage]:
        raise NotImplementedError

    @abstractmethod
    def delete_language(
        self,
        user_id: str,
        language_id: str,
    ) -> bool:
        raise NotImplementedError


class SqlCandidateLanguageRepository(CandidateLanguageRepository):
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
        self.credential = AzureCliCredential()

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
    def _map_row(row) -> CandidateLanguage:
        return CandidateLanguage(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            language_name=row.language_name,
            speaking_proficiency=row.speaking_proficiency,
            reading_proficiency=row.reading_proficiency,
            writing_proficiency=row.writing_proficiency,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_languages(
        self,
        user_id: str,
    ) -> list[CandidateLanguage]:

        sql = """
        SELECT
            l.id,
            l.candidate_id,
            l.language_name,
            l.speaking_proficiency,
            l.reading_proficiency,
            l.writing_proficiency,
            l.created_at,
            l.updated_at
        FROM dbo.candidate_languages AS l
        INNER JOIN dbo.candidates AS c
            ON c.id = l.candidate_id
        WHERE c.entra_object_id = ?
        ORDER BY
            l.language_name ASC,
            l.created_at ASC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, user_id)
            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def create_language(
        self,
        user_id: str,
        language_name: str,
        speaking_proficiency: Optional[str],
        reading_proficiency: Optional[str],
        writing_proficiency: Optional[str],
    ) -> CandidateLanguage:

        sql = """
        INSERT INTO dbo.candidate_languages (
            candidate_id,
            language_name,
            speaking_proficiency,
            reading_proficiency,
            writing_proficiency
        )
        OUTPUT
            INSERTED.id,
            INSERTED.candidate_id,
            INSERTED.language_name,
            INSERTED.speaking_proficiency,
            INSERTED.reading_proficiency,
            INSERTED.writing_proficiency,
            INSERTED.created_at,
            INSERTED.updated_at
        SELECT
            c.id,
            ?,
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
                language_name,
                speaking_proficiency,
                reading_proficiency,
                writing_proficiency,
                user_id,
            )

            row = cursor.fetchone()

            if row is None:
                raise ValueError("Candidate profile was not found.")

            connection.commit()

        return self._map_row(row)

    def update_language(
        self,
        user_id: str,
        language_id: str,
        language_name: str,
        speaking_proficiency: Optional[str],
        reading_proficiency: Optional[str],
        writing_proficiency: Optional[str],
    ) -> Optional[CandidateLanguage]:

        sql = """
        UPDATE l
        SET
            language_name = ?,
            speaking_proficiency = ?,
            reading_proficiency = ?,
            writing_proficiency = ?,
            updated_at = SYSUTCDATETIME()
        OUTPUT
            INSERTED.id,
            INSERTED.candidate_id,
            INSERTED.language_name,
            INSERTED.speaking_proficiency,
            INSERTED.reading_proficiency,
            INSERTED.writing_proficiency,
            INSERTED.created_at,
            INSERTED.updated_at
        FROM dbo.candidate_languages AS l
        INNER JOIN dbo.candidates AS c
            ON c.id = l.candidate_id
        WHERE l.id = ?
          AND c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                language_name,
                speaking_proficiency,
                reading_proficiency,
                writing_proficiency,
                language_id,
                user_id,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            connection.commit()

        return self._map_row(row)

    def delete_language(
        self,
        user_id: str,
        language_id: str,
    ) -> bool:

        sql = """
        DELETE l
        FROM dbo.candidate_languages AS l
        INNER JOIN dbo.candidates AS c
            ON c.id = l.candidate_id
        WHERE l.id = ?
          AND c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                language_id,
                user_id,
            )

            deleted = cursor.rowcount > 0
            connection.commit()

        return deleted
