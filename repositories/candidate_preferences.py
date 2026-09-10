from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.candidate_preferences import CandidatePreferences


class CandidatePreferencesRepository(ABC):

    @abstractmethod
    def get_preferences(
        self,
        candidate_id: str,
    ) -> Optional[CandidatePreferences]:
        raise NotImplementedError

    @abstractmethod
    def save_preferences(
        self,
        candidate_id: str,
        preferred_job_title: str | None,
        preferred_location: str | None,
        preferred_employment_type: str | None,
        work_arrangement: str | None,
        expected_salary: float | None,
        currency: str | None,
        availability_notice_period: str | None,
        open_to_relocation: bool | None,
        available_for_recruitment: bool,
        preferred_contact_method: str | None,
    ) -> CandidatePreferences:
        raise NotImplementedError


class SqlCandidatePreferencesRepository(CandidatePreferencesRepository):
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
    def _map_row(row) -> CandidatePreferences:
        return CandidatePreferences(
            id=str(row[0]),
            candidate_id=str(row[1]),
            preferred_job_title=row[2],
            preferred_location=row[3],
            preferred_employment_type=row[4],
            work_arrangement=row[5],
            expected_salary=(
                float(row[6])
                if row[6] is not None
                else None
            ),
            currency=row[7],
            availability_notice_period=row[8],
            open_to_relocation=(
                bool(row[9])
                if row[9] is not None
                else None
            ),
            available_for_recruitment=bool(row[10]),
            preferred_contact_method=row[11],
            created_at=row[12],
            updated_at=row[13],
        )

    def get_preferences(
        self,
        candidate_id: str,
    ) -> Optional[CandidatePreferences]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.candidate_id,
                    p.preferred_job_title,
                    p.preferred_location,
                    p.preferred_employment_type,
                    p.work_arrangement,
                    p.expected_salary,
                    p.currency,
                    p.availability_notice_period,
                    p.open_to_relocation,
                    p.available_for_recruitment,
                    p.preferred_contact_method,
                    p.created_at,
                    p.updated_at
                FROM dbo.candidate_preferences AS p
                INNER JOIN dbo.candidates AS c
                    ON c.id = p.candidate_id
                WHERE c.entra_object_id = ?;
                """,
                candidate_id,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._map_row(row)

    def save_preferences(
        self,
        candidate_id: str,
        preferred_job_title: str | None,
        preferred_location: str | None,
        preferred_employment_type: str | None,
        work_arrangement: str | None,
        expected_salary: float | None,
        currency: str | None,
        availability_notice_period: str | None,
        open_to_relocation: bool | None,
        available_for_recruitment: bool,
        preferred_contact_method: str | None,
    ) -> CandidatePreferences:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT c.id
                FROM dbo.candidates AS c
                WHERE c.entra_object_id = ?;
                """,
                candidate_id,
            )

            candidate = cursor.fetchone()

            if candidate is None:
                raise ValueError("Candidate profile not found")

            cursor.execute(
                """
                UPDATE dbo.candidate_preferences
                SET
                    preferred_job_title = ?,
                    preferred_location = ?,
                    preferred_employment_type = ?,
                    work_arrangement = ?,
                    expected_salary = ?,
                    currency = ?,
                    availability_notice_period = ?,
                    open_to_relocation = ?,
                    available_for_recruitment = ?,
                    preferred_contact_method = ?,
                    updated_at = SYSUTCDATETIME()
                OUTPUT
                    INSERTED.id,
                    INSERTED.candidate_id,
                    INSERTED.preferred_job_title,
                    INSERTED.preferred_location,
                    INSERTED.preferred_employment_type,
                    INSERTED.work_arrangement,
                    INSERTED.expected_salary,
                    INSERTED.currency,
                    INSERTED.availability_notice_period,
                    INSERTED.open_to_relocation,
                    INSERTED.available_for_recruitment,
                    INSERTED.preferred_contact_method,
                    INSERTED.created_at,
                    INSERTED.updated_at
                WHERE candidate_id = ?;
                """,
                preferred_job_title,
                preferred_location,
                preferred_employment_type,
                work_arrangement,
                expected_salary,
                currency,
                availability_notice_period,
                open_to_relocation,
                available_for_recruitment,
                preferred_contact_method,
                candidate.id,
            )

            row = cursor.fetchone()

            if row is None:
                cursor.execute(
                    """
                    INSERT INTO dbo.candidate_preferences (
                        candidate_id,
                        preferred_job_title,
                        preferred_location,
                        preferred_employment_type,
                        work_arrangement,
                        expected_salary,
                        currency,
                        availability_notice_period,
                        open_to_relocation,
                        available_for_recruitment,
                        preferred_contact_method
                    )
                    OUTPUT
                        INSERTED.id,
                        INSERTED.candidate_id,
                        INSERTED.preferred_job_title,
                        INSERTED.preferred_location,
                        INSERTED.preferred_employment_type,
                        INSERTED.work_arrangement,
                        INSERTED.expected_salary,
                        INSERTED.currency,
                        INSERTED.availability_notice_period,
                        INSERTED.open_to_relocation,
                        INSERTED.available_for_recruitment,
                        INSERTED.preferred_contact_method,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    candidate.id,
                    preferred_job_title,
                    preferred_location,
                    preferred_employment_type,
                    work_arrangement,
                    expected_salary,
                    currency,
                    availability_notice_period,
                    open_to_relocation,
                    available_for_recruitment,
                    preferred_contact_method,
                )

                row = cursor.fetchone()

            if row is None:
                raise RuntimeError(
                    "Candidate preferences could not be saved"
                )

            conn.commit()
            return self._map_row(row)
