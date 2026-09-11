from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

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

    @abstractmethod
    def list_candidate_applications(
        self,
        candidate_id: str,
    ) -> list[EmployerApplication]:
        raise NotImplementedError

    @abstractmethod
    def create_application(
        self,
        candidate_id: str,
        job_id: str,
        cover_letter: Optional[str] = None,
    ) -> EmployerApplication:
        raise NotImplementedError


class SqlApplicationRepository(ApplicationRepository):

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

    @staticmethod
    def _application_select() -> str:
        return """
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
        """

    def list_applications(
        self,
        organization_id: str,
    ) -> list[EmployerApplication]:
        sql = (
            self._application_select()
            + """
            WHERE j.organization_id = ?
            ORDER BY a.applied_at DESC;
            """
        )

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
        sql = (
            self._application_select()
            + """
            WHERE a.id = ?
              AND j.organization_id = ?;
            """
        )

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

    def list_candidate_applications(
        self,
        candidate_id: str,
    ) -> list[EmployerApplication]:
        sql = (
            self._application_select()
            + """
            WHERE a.candidate_id = ?
            ORDER BY a.applied_at DESC;
            """
        )

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, candidate_id)
            rows = cursor.fetchall()

        return [
            self._map_row(row)
            for row in rows
        ]

    def create_application(
        self,
        candidate_id: str,
        job_id: str,
        cover_letter: Optional[str] = None,
    ) -> EmployerApplication:
        insert_sql = """
            INSERT INTO dbo.applications (
                candidate_id,
                job_id,
                cover_letter
            )
            OUTPUT INSERTED.id
            VALUES (?, ?, ?);
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                insert_sql,
                candidate_id,
                job_id,
                cover_letter,
            )

            inserted_row = cursor.fetchone()

            if inserted_row is None:
                raise RuntimeError(
                    "Application could not be created"
                )

            application_id = str(inserted_row.id)

            select_sql = (
                self._application_select()
                + """
                WHERE a.id = ?;
                """
            )

            cursor.execute(
                select_sql,
                application_id,
            )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError(
                    "Created application could not be retrieved"
                )

            connection.commit()

        return self._map_row(row)
