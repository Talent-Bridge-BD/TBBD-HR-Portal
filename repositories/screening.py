from abc import ABC, abstractmethod
from datetime import datetime

from azure.identity import DefaultAzureCredential
import pyodbc

from models.screening import ScreeningAssessment


class ScreeningRepository(ABC):

    @abstractmethod
    def get_by_application(
        self,
        application_id: str,
    ) -> ScreeningAssessment | None:
        ...

    @abstractmethod
    def create(
        self,
        application_id: str,
        basic_eligibility: str | None = None,
        relevant_experience: str | None = None,
        education: str | None = None,
        communication: str | None = None,
        availability: str | None = None,
        screening_notes: str | None = None,
        recommendation: str | None = None,
    ) -> ScreeningAssessment:
        ...

    @abstractmethod
    def update(
        self,
        screening_id: str,
        basic_eligibility: str | None = None,
        relevant_experience: str | None = None,
        education: str | None = None,
        communication: str | None = None,
        availability: str | None = None,
        screening_notes: str | None = None,
        recommendation: str | None = None,
    ) -> ScreeningAssessment | None:
        ...


class SqlScreeningRepository(ScreeningRepository):

    def __init__(self):
        self.server = "tbbd-sql-sea.database.windows.net"
        self.database = "tbbd-hr-db"
        self.credential = DefaultAzureCredential()

    def _get_connection(self):
        token = self.credential.get_token(
            "https://database.windows.net/.default"
        )

        token_bytes = token.token.encode("utf-16-le")
        token_struct = (
            len(token_bytes).to_bytes(4, byteorder="little")
            + token_bytes
        )

        return pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;",
            attrs_before={1256: token_struct},
        )

    @staticmethod
    def _map_row(row) -> ScreeningAssessment:
        return ScreeningAssessment(
            id=str(row.id),
            application_id=str(row.application_id),
            basic_eligibility=row.basic_eligibility,
            relevant_experience=row.relevant_experience,
            education=row.education,
            communication=row.communication,
            availability=row.availability,
            screening_notes=row.screening_notes,
            recommendation=row.recommendation,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _select_sql() -> str:
        return """
            SELECT
                id,
                application_id,
                basic_eligibility,
                relevant_experience,
                education,
                communication,
                availability,
                screening_notes,
                recommendation,
                created_at,
                updated_at
            FROM dbo.screening_assessments
        """

    def get_by_application(
        self,
        application_id: str,
    ) -> ScreeningAssessment | None:

        with self._get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                self._select_sql() + """
                    WHERE application_id = ?
                """,
                application_id,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._map_row(row)

    def create(
        self,
        application_id: str,
        basic_eligibility: str | None = None,
        relevant_experience: str | None = None,
        education: str | None = None,
        communication: str | None = None,
        availability: str | None = None,
        screening_notes: str | None = None,
        recommendation: str | None = None,
    ) -> ScreeningAssessment:

        with self._get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.screening_assessments (
                    application_id,
                    basic_eligibility,
                    relevant_experience,
                    education,
                    communication,
                    availability,
                    screening_notes,
                    recommendation
                )
                OUTPUT
                    INSERTED.id,
                    INSERTED.application_id,
                    INSERTED.basic_eligibility,
                    INSERTED.relevant_experience,
                    INSERTED.education,
                    INSERTED.communication,
                    INSERTED.availability,
                    INSERTED.screening_notes,
                    INSERTED.recommendation,
                    INSERTED.created_at,
                    INSERTED.updated_at
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                application_id,
                basic_eligibility,
                relevant_experience,
                education,
                communication,
                availability,
                screening_notes,
                recommendation,
            )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError(
                    "Screening assessment was not created."
                )

            connection.commit()

            return self._map_row(row)

    def update(
        self,
        screening_id: str,
        basic_eligibility: str | None = None,
        relevant_experience: str | None = None,
        education: str | None = None,
        communication: str | None = None,
        availability: str | None = None,
        screening_notes: str | None = None,
        recommendation: str | None = None,
    ) -> ScreeningAssessment | None:

        with self._get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE dbo.screening_assessments
                SET
                    basic_eligibility = ?,
                    relevant_experience = ?,
                    education = ?,
                    communication = ?,
                    availability = ?,
                    screening_notes = ?,
                    recommendation = ?,
                    updated_at = SYSUTCDATETIME()
                OUTPUT
                    INSERTED.id,
                    INSERTED.application_id,
                    INSERTED.basic_eligibility,
                    INSERTED.relevant_experience,
                    INSERTED.education,
                    INSERTED.communication,
                    INSERTED.availability,
                    INSERTED.screening_notes,
                    INSERTED.recommendation,
                    INSERTED.created_at,
                    INSERTED.updated_at
                WHERE id = ?
                """,
                basic_eligibility,
                relevant_experience,
                education,
                communication,
                availability,
                screening_notes,
                recommendation,
                screening_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                return None

            connection.commit()

            return self._map_row(row)
