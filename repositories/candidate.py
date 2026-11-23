from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import AzureCliCredential, DefaultAzureCredential

from models.candidate import CandidateProfile


class CandidateRepository(ABC):

    @abstractmethod
    def get_candidate_id(self, user_id: str) -> Optional[str]:
        raise NotImplementedError

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

    def get_candidate_id(self, user_id: str) -> Optional[str]:
        profile = self._profiles.get(user_id)
        return profile.user_id if profile else None


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
        if os.environ.get("WEBSITE_SITE_NAME"):
            self.credential = DefaultAzureCredential()
        else:
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
    def _sql_date(value):
        """Convert an optional ISO date or datetime to a SQL date."""
        from datetime import date, datetime

        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))

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
            date_of_birth=(
                row.date_of_birth.isoformat()
                if row.date_of_birth is not None else None
            ),
            gender=row.gender or "",
            nationality=row.nationality or "Bangladeshi",
            nid_number=row.nid_number or "",
            full_address=row.address or "",
            professional_title=row.current_title or "",
            summary=row.professional_summary or "",
            location=", ".join(
                part for part in (row.city or "", row.country or "") if part
            ),
            career_level=row.career_level or "",
            years_experience=(
                float(row.years_experience)
                if row.years_experience is not None else None
            ),
            passport_number=row.passport_number or "",
            passport_country=row.passport_country or "",
            passport_issue_date=(
                row.passport_issue_date.isoformat()
                if row.passport_issue_date is not None else None
            ),
            passport_expiry_date=(
                row.passport_expiry_date.isoformat()
                if row.passport_expiry_date is not None else None
            ),
            passport_status=row.passport_status or "",
            international_travel_readiness=(
                row.international_travel_readiness or ""
            ),
            workflow_status=row.workflow_status or "Applied",
            resume_document_id=resume_document_id,
        )

    @staticmethod
    def _split_location(location: str) -> tuple[Optional[str], Optional[str]]:
        if not location:
            return None, None

        parts = [part.strip() for part in location.split(",", 1)]

        city = parts[0] or None
        country = parts[1] if len(parts) > 1 and parts[1] else None

        return city, country

    def get_candidate_id(self, user_id: str) -> Optional[str]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id
                FROM dbo.candidates
                WHERE entra_object_id = ?
                """,
                user_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return str(row.id)

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
                    date_of_birth,
                    address,
                    gender,
                    nationality,
                    nid_number,
                    city,
                    country,
                    professional_summary,
                    current_title,
                    career_level,
                    years_experience,
                    passport_number,
                    passport_country,
                    passport_issue_date,
                    passport_expiry_date,
                    passport_status,
                    international_travel_readiness,
                    workflow_status
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
                if document_row is not None else None
            )
            return self._row_to_profile(row, resume_document_id)

    def save_profile(self, profile: CandidateProfile) -> CandidateProfile:
        city, country = self._split_location(profile.location)
        date_of_birth = self._sql_date(profile.date_of_birth)
        passport_expiry_date = self._sql_date(profile.passport_expiry_date)

        output_columns = """
            INSERTED.id,
            INSERTED.entra_object_id,
            INSERTED.first_name,
            INSERTED.last_name,
            INSERTED.email,
            INSERTED.phone,
            INSERTED.date_of_birth,
            INSERTED.address,
            INSERTED.city,
            INSERTED.country,
            INSERTED.professional_summary,
            INSERTED.current_title,
            INSERTED.career_level,
            INSERTED.years_experience,
            INSERTED.passport_number,
            INSERTED.passport_country,
            INSERTED.gender,
            INSERTED.nationality,
            INSERTED.nid_number,
            INSERTED.passport_issue_date,
            INSERTED.passport_expiry_date,
            INSERTED.passport_status,
            INSERTED.international_travel_readiness,
            INSERTED.workflow_status
        """

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
                    f"""
                    INSERT INTO dbo.candidates (
                        entra_object_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        date_of_birth,
                        address,
                        city,
                        country,
                        current_title,
                        professional_summary,
                        career_level,
                        years_experience,
                        passport_number,
                        passport_country,
                        gender,
                        nationality,
                        nid_number,
                        passport_issue_date,
                        passport_expiry_date,
                        passport_status,
                        international_travel_readiness,
                        workflow_status,
                        profile_status
                    )
                    OUTPUT {output_columns}
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                    """,
                    profile.user_id,
                    profile.first_name,
                    profile.last_name or "",
                    profile.email,
                    profile.phone or None,
                    date_of_birth,
                    profile.full_address or None,
                    city,
                    country,
                    profile.professional_title or None,
                    profile.summary or None,
                    profile.career_level or None,
                    profile.years_experience,
                    profile.passport_number or None,
                    profile.passport_country or None,
                    profile.gender or None,
                    profile.nationality or "Bangladeshi",
                    profile.nid_number or None,
                    self._sql_date(profile.passport_issue_date),
                    passport_expiry_date,
                    profile.passport_status or None,
                    profile.international_travel_readiness or None,
                    profile.workflow_status or "Applied",
                    "incomplete",
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE dbo.candidates
                    SET
                        first_name = ?,
                        last_name = ?,
                        email = ?,
                        phone = ?,
                        date_of_birth = ?,
                        address = ?,
                        city = ?,
                        country = ?,
                        current_title = ?,
                        professional_summary = ?,
                        career_level = ?,
                        years_experience = ?,
                        passport_number = ?,
                        passport_country = ?,
                        gender = ?,
                        nationality = ?,
                        nid_number = ?,
                        passport_issue_date = ?,
                        passport_expiry_date = ?,
                        passport_status = ?,
                        international_travel_readiness = ?,
                        workflow_status = ?,
                        updated_at = SYSUTCDATETIME()
                    OUTPUT {output_columns}
                    WHERE id = ?
                    """,
                    profile.first_name,
                    profile.last_name or "",
                    profile.email,
                    profile.phone or None,
                    date_of_birth,
                    profile.full_address or None,
                    city,
                    country,
                    profile.professional_title or None,
                    profile.summary or None,
                    profile.career_level or None,
                    profile.years_experience,
                    profile.passport_number or None,
                    profile.passport_country or None,
                    profile.gender or None,
                    profile.nationality or "Bangladeshi",
                    profile.nid_number or None,
                    self._sql_date(profile.passport_issue_date),
                    passport_expiry_date,
                    profile.passport_status or None,
                    profile.international_travel_readiness or None,
                    profile.workflow_status or "Applied",
                    existing.id,
                )

            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("Candidate profile could not be saved")

            connection.commit()
            return self._row_to_profile(row, profile.resume_document_id)
