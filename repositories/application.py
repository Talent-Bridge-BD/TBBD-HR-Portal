from abc import ABC, abstractmethod
from typing import Optional

from azure.identity import DefaultAzureCredential
import pyodbc

from models.application import EmployerApplication


class ApplicationRepository(ABC):

    @abstractmethod
    def list_applications(
        self,
        organization_id: str,
    ) -> list[EmployerApplication]:
        raise NotImplementedError

    @abstractmethod
    def get_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> Optional[EmployerApplication]:
        raise NotImplementedError


class SqlApplicationRepository(ApplicationRepository):

    def __init__(self):
        self.server = "tbbd-sql-sea.database.windows.net"
        self.database = "tbbd-hr-db"
        self.credential = DefaultAzureCredential()

    def _connection(self):
        token = self.credential.get_token(
            "https://database.windows.net/.default"
        ).token

        token_bytes = token.encode("utf-16-le")
        token_struct = (
            len(token_bytes).to_bytes(4, "little")
            + token_bytes
        )

        return pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;",
            attrs_before={1256: token_struct},
        )

    @staticmethod
    def _map_row(row) -> EmployerApplication:
        return EmployerApplication(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            job_id=str(row.job_id),
            candidate_first_name=row.first_name,
            candidate_last_name=row.last_name,
            candidate_email=row.email,
            candidate_phone=row.phone,
            job_title=row.job_title,
            status=row.status,
            cover_letter=row.cover_letter,
            applied_at=row.applied_at,
            updated_at=row.updated_at,
        )

    def list_applications(
        self,
        organization_id: str,
    ) -> list[EmployerApplication]:
        sql = """
            SELECT
                a.id,
                a.candidate_id,
                a.job_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                j.title AS job_title,
                a.status,
                a.cover_letter,
                a.applied_at,
                a.updated_at
            FROM dbo.applications AS a
            INNER JOIN dbo.candidates AS c
                ON c.id = a.candidate_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE j.organization_id = ?
            ORDER BY a.applied_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, organization_id)
            rows = cursor.fetchall()

        return [
            self._map_row(row)
            for row in rows
        ]

    def get_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> Optional[EmployerApplication]:
        sql = """
            SELECT
                a.id,
                a.candidate_id,
                a.job_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                j.title AS job_title,
                a.status,
                a.cover_letter,
                a.applied_at,
                a.updated_at
            FROM dbo.applications AS a
            INNER JOIN dbo.candidates AS c
                ON c.id = a.candidate_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE a.id = ?
              AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)


