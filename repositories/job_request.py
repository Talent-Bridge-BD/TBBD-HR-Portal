from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.job_request import JobRequest


class JobRequestRepository(ABC):
    @abstractmethod
    def list_requests(self, organization_id: str) -> list[JobRequest]:
        raise NotImplementedError

    @abstractmethod
    def get_request(
        self,
        organization_id: str,
        request_id: str,
    ) -> Optional[JobRequest]:
        raise NotImplementedError

    @abstractmethod
    def save_request(self, request: JobRequest) -> JobRequest:
        raise NotImplementedError


class SqlJobRequestRepository(JobRequestRepository):
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
    def _row_to_request(row: pyodbc.Row) -> JobRequest:
        return JobRequest(
            id=str(row.id),
            organization_id=str(row.organization_id),
            requested_by=row.requested_by,
            title=row.title,
            description=row.description,
            employment_type=row.employment_type,
            location=row.location,
            country=row.country,
            number_of_positions=row.number_of_positions,
            status=row.status,
            requested_at=row.requested_at,
            reviewed_at=row.reviewed_at,
            reviewed_by=row.reviewed_by,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_requests(
        self,
        organization_id: str,
    ) -> list[JobRequest]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    organization_id,
                    requested_by,
                    title,
                    description,
                    employment_type,
                    location,
                    country,
                    number_of_positions,
                    status,
                    requested_at,
                    reviewed_at,
                    reviewed_by,
                    created_at,
                    updated_at
                FROM dbo.job_requests
                WHERE organization_id = ?
                ORDER BY created_at DESC
                """,
                organization_id,
            )

            return [
                self._row_to_request(row)
                for row in cursor.fetchall()
            ]

    def get_request(
        self,
        organization_id: str,
        request_id: str,
    ) -> Optional[JobRequest]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    organization_id,
                    requested_by,
                    title,
                    description,
                    employment_type,
                    location,
                    country,
                    number_of_positions,
                    status,
                    requested_at,
                    reviewed_at,
                    reviewed_by,
                    created_at,
                    updated_at
                FROM dbo.job_requests
                WHERE organization_id = ?
                  AND id = ?
                """,
                organization_id,
                request_id,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_request(row)

    def save_request(
        self,
        request: JobRequest,
    ) -> JobRequest:
        with self._connection() as connection:
            cursor = connection.cursor()

            if request.id:
                cursor.execute(
                    """
                    SELECT id
                    FROM dbo.job_requests
                    WHERE id = ?
                      AND organization_id = ?
                    """,
                    request.id,
                    request.organization_id,
                )
                existing = cursor.fetchone()
            else:
                existing = None

            if existing is None:
                cursor.execute(
                    """
                    INSERT INTO dbo.job_requests (
                        organization_id,
                        requested_by,
                        title,
                        description,
                        employment_type,
                        location,
                        country,
                        number_of_positions,
                        status,
                        requested_at
                    )
                    OUTPUT
                        INSERTED.id,
                        INSERTED.organization_id,
                        INSERTED.requested_by,
                        INSERTED.title,
                        INSERTED.description,
                        INSERTED.employment_type,
                        INSERTED.location,
                        INSERTED.country,
                        INSERTED.number_of_positions,
                        INSERTED.status,
                        INSERTED.requested_at,
                        INSERTED.reviewed_at,
                        INSERTED.reviewed_by,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    request.organization_id,
                    request.requested_by,
                    request.title,
                    request.description,
                    request.employment_type,
                    request.location,
                    request.country,
                    request.number_of_positions,
                    request.status,
                    request.requested_at,
                )
            else:
                cursor.execute(
                    """
                    UPDATE dbo.job_requests
                    SET
                        title = ?,
                        description = ?,
                        employment_type = ?,
                        location = ?,
                        country = ?,
                        number_of_positions = ?,
                        status = ?,
                        reviewed_at = ?,
                        reviewed_by = ?,
                        updated_at = SYSUTCDATETIME()
                    OUTPUT
                        INSERTED.id,
                        INSERTED.organization_id,
                        INSERTED.requested_by,
                        INSERTED.title,
                        INSERTED.description,
                        INSERTED.employment_type,
                        INSERTED.location,
                        INSERTED.country,
                        INSERTED.number_of_positions,
                        INSERTED.status,
                        INSERTED.requested_at,
                        INSERTED.reviewed_at,
                        INSERTED.reviewed_by,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    WHERE id = ?
                      AND organization_id = ?
                    """,
                    request.title,
                    request.description,
                    request.employment_type,
                    request.location,
                    request.country,
                    request.number_of_positions,
                    request.status,
                    request.reviewed_at,
                    request.reviewed_by,
                    request.id,
                    request.organization_id,
                )

            row = cursor.fetchone()
            connection.commit()

            if row is None:
                raise RuntimeError(
                    "Job request save did not return a database row"
                )

            return self._row_to_request(row)
