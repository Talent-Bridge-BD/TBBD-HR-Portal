from __future__ import annotations

import os
import struct
from uuid import UUID

from azure.identity import AzureCliCredential, DefaultAzureCredential
import pyodbc


class EmployerAccessRequestRepository:
    SQL_ACCESS_TOKEN_ATTRIBUTE = 1256
    SQL_SCOPE = "https://database.windows.net/.default"

    ALLOWED_STATUSES = {"Pending", "Approved", "Rejected"}

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

    def _connection(self):
        token = self.credential.get_token(
            self.SQL_SCOPE
        ).token
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
    def _serialize(row) -> dict:
        return {
            "id": str(row.id),
            "company_name": row.company_name,
            "representative_name": row.representative_name,
            "email": row.email,
            "phone": row.phone,
            "country": row.country,
            "industry": row.industry,
            "requested_roles": row.requested_roles,
            "requirements": row.requirements,
            "status": row.status,
            "reviewed_by": row.reviewed_by,
            "reviewed_at": (
                row.reviewed_at.isoformat()
                if row.reviewed_at
                else None
            ),
            "review_notes": row.review_notes,
            "created_at": (
                row.created_at.isoformat()
                if row.created_at
                else None
            ),
            "updated_at": (
                row.updated_at.isoformat()
                if row.updated_at
                else None
            ),
        }

    def create_request(
        self,
        *,
        company_name: str,
        representative_name: str,
        email: str,
        phone: str | None = None,
        country: str | None = None,
        industry: str | None = None,
        requested_roles: str | None = None,
        requirements: str | None = None,
    ) -> dict:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO dbo.employer_access_requests (
                    company_name,
                    representative_name,
                    email,
                    phone,
                    country,
                    industry,
                    requested_roles,
                    requirements
                )
                OUTPUT
                    INSERTED.id,
                    INSERTED.company_name,
                    INSERTED.representative_name,
                    INSERTED.email,
                    INSERTED.phone,
                    INSERTED.country,
                    INSERTED.industry,
                    INSERTED.requested_roles,
                    INSERTED.requirements,
                    INSERTED.status,
                    INSERTED.reviewed_by,
                    INSERTED.reviewed_at,
                    INSERTED.review_notes,
                    INSERTED.created_at,
                    INSERTED.updated_at
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                company_name,
                representative_name,
                email,
                phone,
                country,
                industry,
                requested_roles,
                requirements,
            )
            row = cursor.fetchone()
            connection.commit()

            if row is None:
                raise RuntimeError(
                    "Request was not returned after insertion"
                )

            return self._serialize(row)

    def list_requests(
        self,
        *,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        if status is not None and status not in self.ALLOWED_STATUSES:
            raise ValueError("Invalid request status")

        limit = max(1, min(limit, 500))

        query = """
            SELECT TOP (?)
                id,
                company_name,
                representative_name,
                email,
                phone,
                country,
                industry,
                requested_roles,
                requirements,
                status,
                reviewed_by,
                reviewed_at,
                review_notes,
                created_at,
                updated_at
            FROM dbo.employer_access_requests
        """
        parameters: list = [limit]

        if status is not None:
            query += " WHERE status = ?"
            parameters.append(status)

        query += " ORDER BY created_at DESC"

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, *parameters)
            return [
                self._serialize(row)
                for row in cursor.fetchall()
            ]

    def review_request(
        self,
        request_id: str,
        *,
        status: str,
        reviewed_by: str,
        review_notes: str | None = None,
    ) -> dict | None:
        if status not in {"Approved", "Rejected"}:
            raise ValueError(
                "Review status must be Approved or Rejected"
            )

        try:
            parsed_id = str(UUID(request_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("Invalid request ID") from None

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE dbo.employer_access_requests
                SET
                    status = ?,
                    reviewed_by = ?,
                    reviewed_at = SYSUTCDATETIME(),
                    review_notes = ?,
                    updated_at = SYSUTCDATETIME()
                OUTPUT
                    INSERTED.id,
                    INSERTED.company_name,
                    INSERTED.representative_name,
                    INSERTED.email,
                    INSERTED.phone,
                    INSERTED.country,
                    INSERTED.industry,
                    INSERTED.requested_roles,
                    INSERTED.requirements,
                    INSERTED.status,
                    INSERTED.reviewed_by,
                    INSERTED.reviewed_at,
                    INSERTED.review_notes,
                    INSERTED.created_at,
                    INSERTED.updated_at
                WHERE id = ? AND status = N'Pending'
                """,
                status,
                reviewed_by,
                review_notes,
                parsed_id,
            )
            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                return None

            connection.commit()
            return self._serialize(row)
