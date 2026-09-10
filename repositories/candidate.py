from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

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


class SqlCandidateRepository(CandidateRepository):
    """
    Azure SQL implementation using Microsoft Entra authentication.

    The production App Service uses its System Assigned Managed Identity.
    Local development can use DefaultAzureCredential (for example, Azure CLI).
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
    def _row_to_profile(
        row: pyodbc.Row,
        resume_document_id: Optional[str] = None,
    ) -> CandidateProfile:
        return CandidateProfile(
            user_id=row.entra_object_id,
            first_name=row.first_name or "",
            last_name=row.last_name or "",
            email=row.email or "",
            phone=row.phone or "",
            professional_title=row.current_title or "",
            summary=row.professional_summary or "",
            location="",
            resume_document_id=resume_document_id,
        )

    def get_profile(self, user_id: str) -> Optional[CandidateProfile]:
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    entra_object_id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    professional_summary,
                    current_title
                FROM dbo.candidates
                WHERE entra_object_id = ?
                """,
                user_id,
            )
            row = cursor.fetchone()

            if row is None:
                return None

            cursor.execute(
                """
                SELECT TOP (1)
                    CONVERT(nvarchar(36), id) AS document_id
                FROM dbo.documents
                WHERE candidate_id = ?
                  AND document_type = N'resume'
                ORDER BY created_at DESC
                """,
                row.id,
            )
            document_row = cursor.fetchone()

            resume_document_id = (
                str(document_row.document_id)
                if document_row is not None
                else None
            )

            return self._row_to_profile(row, resume_document_id)

    def save_profile(self, profile: CandidateProfile) -> CandidateProfile:
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id
                FROM dbo.candidates
                WHERE entra_object_id = ?
                """,
                profile.user_id,
            )
            existing = cursor.fetchone()

            if existing is None:
                cursor.execute(
                    """
                    INSERT INTO dbo.candidates (
                        entra_object_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        current_title,
                        professional_summary,
                        profile_status
                    )
                    OUTPUT
                        INSERTED.id,
                        INSERTED.entra_object_id,
                        INSERTED.first_name,
                        INSERTED.last_name,
                        INSERTED.email,
                        INSERTED.phone,
                        INSERTED.professional_summary,
                        INSERTED.current_title
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    profile.user_id,
                    profile.first_name,
                    profile.last_name,
                    profile.email,
                    profile.phone or None,
                    profile.professional_title or None,
                    profile.summary or None,
                    "incomplete",
                )
            else:
                cursor.execute(
                    """
                    UPDATE dbo.candidates
                    SET
                        first_name = ?,
                        last_name = ?,
                        email = ?,
                        phone = ?,
                        current_title = ?,
                        professional_summary = ?,
                        updated_at = SYSUTCDATETIME()
                    OUTPUT
                        INSERTED.id,
                        INSERTED.entra_object_id,
                        INSERTED.first_name,
                        INSERTED.last_name,
                        INSERTED.email,
                        INSERTED.phone,
                        INSERTED.professional_summary,
                        INSERTED.current_title
                    WHERE id = ?
                    """,
                    profile.first_name,
                    profile.last_name,
                    profile.email,
                    profile.phone or None,
                    profile.professional_title or None,
                    profile.summary or None,
                    existing.id,
                )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError("Candidate profile could not be saved")

            connection.commit()

            return self._row_to_profile(
                row,
                profile.resume_document_id,
            )
