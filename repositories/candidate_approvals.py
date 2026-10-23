from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Any

import pyodbc
from azure.identity import AzureCliCredential, DefaultAzureCredential


class CandidateApprovalRepository(ABC):
    """Persistence interface for candidate access approval."""

    @abstractmethod
    def ensure_candidate(self, entra_object_id: str) -> dict:
        """Create a pending record if one does not already exist."""
        raise NotImplementedError

    @abstractmethod
    def get_approval(self, entra_object_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def list_approvals(
        self,
        *,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def review_candidate(
        self,
        entra_object_id: str,
        *,
        status: str,
        reviewed_by: str,
        approval_notes: str | None = None,
    ) -> dict | None:
        raise NotImplementedError


class InMemoryCandidateApprovalRepository(CandidateApprovalRepository):
    """Isolated implementation for unit tests."""

    ALLOWED_STATUSES = {"pending", "approved", "rejected"}

    def __init__(self):
        self._records: dict[str, dict[str, Any]] = {}

    def ensure_candidate(self, entra_object_id: str) -> dict:
        entra_object_id = self._validate_identity(entra_object_id)

        if entra_object_id not in self._records:
            self._records[entra_object_id] = {
                "entra_object_id": entra_object_id,
                "approval_status": "pending",
                "reviewed_by": None,
                "reviewed_at": None,
                "approval_notes": None,
                "created_at": None,
                "updated_at": None,
            }

        return dict(self._records[entra_object_id])

    def get_approval(self, entra_object_id: str) -> dict | None:
        entra_object_id = self._validate_identity(entra_object_id)
        record = self._records.get(entra_object_id)
        return dict(record) if record else None

    def list_approvals(
        self,
        *,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        self._validate_status(status, allow_none=True)
        limit = max(1, min(limit, 500))
        offset = max(0, offset)
        needle = (search or "").strip().casefold()

        records = list(self._records.values())

        if status:
            records = [
                record for record in records
                if record["approval_status"] == status
            ]

        if needle:
            records = [
                record for record in records
                if needle in record["entra_object_id"].casefold()
            ]

        records.sort(
            key=lambda record: (
                record["created_at"] is not None,
                record["created_at"] or "",
                record["entra_object_id"],
            ),
            reverse=True,
        )

        return [
            dict(record)
            for record in records[offset:offset + limit]
        ]

    def review_candidate(
        self,
        entra_object_id: str,
        *,
        status: str,
        reviewed_by: str,
        approval_notes: str | None = None,
    ) -> dict | None:
        entra_object_id = self._validate_identity(entra_object_id)
        self._validate_status(status)

        if status == "pending":
            raise ValueError("Review status must be approved or rejected")

        reviewed_by = reviewed_by.strip()
        if not reviewed_by:
            raise ValueError("Reviewer identity is required")

        record = self._records.get(entra_object_id)

        if record is None or record["approval_status"] != "pending":
            return None

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()
        record.update(
            {
                "approval_status": status,
                "reviewed_by": reviewed_by,
                "reviewed_at": now,
                "approval_notes": approval_notes,
                "updated_at": now,
            }
        )
        return dict(record)

    @staticmethod
    def _validate_identity(entra_object_id: str) -> str:
        value = (entra_object_id or "").strip()
        if not value:
            raise ValueError("Entra object ID is required")
        if len(value) > 200:
            raise ValueError("Entra object ID is too long")
        return value

    @classmethod
    def _validate_status(
        cls,
        status: str | None,
        *,
        allow_none: bool = False,
    ) -> None:
        if allow_none and status is None:
            return
        if status not in cls.ALLOWED_STATUSES:
            raise ValueError("Invalid candidate approval status")


class SqlCandidateApprovalRepository(CandidateApprovalRepository):
    """Azure SQL persistence for candidate approval records."""

    SQL_ACCESS_TOKEN_ATTRIBUTE = 1256
    SQL_SCOPE = "https://database.windows.net/.default"
    ALLOWED_STATUSES = {"pending", "approved", "rejected"}

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
        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER=tcp:{self.server},1433;"
            f"DATABASE={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        # In Azure App Service, let ODBC acquire the managed identity token.
        if os.environ.get("WEBSITE_SITE_NAME"):
            return pyodbc.connect(
                connection_string + "Authentication=ActiveDirectoryMsi;"
            )

        # Keep Azure CLI token authentication for local development.
        token = self.credential.get_token(self.SQL_SCOPE).token
        token_bytes = token.encode("utf-16-le")
        token_struct = struct.pack(
            f"<I{len(token_bytes)}s",
            len(token_bytes),
            token_bytes,
        )

        return pyodbc.connect(
            connection_string,
            attrs_before={
                self.SQL_ACCESS_TOKEN_ATTRIBUTE: token_struct,
            },
        )

    @staticmethod
    def _serialize(row) -> dict:
        first_name = getattr(row, "first_name", None) or ""
        last_name = getattr(row, "last_name", None) or ""

        return {
            "id": str(row.id),
            "entra_object_id": row.entra_object_id,
            "approval_status": row.approval_status,
            "reviewed_by": row.reviewed_by,
            "reviewed_at": (
                row.reviewed_at.isoformat()
                if row.reviewed_at else None
            ),
            "approval_notes": row.approval_notes,
            "created_at": (
                row.created_at.isoformat()
                if row.created_at else None
            ),
            "updated_at": (
                row.updated_at.isoformat()
                if row.updated_at else None
            ),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": " ".join(
                part for part in (first_name, last_name) if part
            ),
            "email": getattr(row, "email", None) or "",
        }

    @staticmethod
    def _validate_identity(entra_object_id: str) -> str:
        value = (entra_object_id or "").strip()
        if not value:
            raise ValueError("Entra object ID is required")
        if len(value) > 200:
            raise ValueError("Entra object ID is too long")
        return value

    @classmethod
    def _validate_status(
        cls,
        status: str | None,
        *,
        allow_none: bool = False,
    ) -> None:
        if allow_none and status is None:
            return
        if status not in cls.ALLOWED_STATUSES:
            raise ValueError("Invalid candidate approval status")

    def ensure_candidate(self, entra_object_id: str) -> dict:
        entra_object_id = self._validate_identity(entra_object_id)

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM dbo.candidate_approvals
                        WITH (UPDLOCK, HOLDLOCK)
                    WHERE entra_object_id = ?
                )
                BEGIN
                    INSERT INTO dbo.candidate_approvals (
                        entra_object_id,
                        approval_status
                    )
                    VALUES (?, N'pending');
                END;

                SELECT
                    id,
                    entra_object_id,
                    approval_status,
                    reviewed_by,
                    reviewed_at,
                    approval_notes,
                    created_at,
                    updated_at
                FROM dbo.candidate_approvals
                WHERE entra_object_id = ?;
                """,
                entra_object_id,
                entra_object_id,
                entra_object_id,
            )
            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise RuntimeError(
                    "Candidate approval record was not returned"
                )

            result = self._serialize(row)
            connection.commit()
            return result

    def get_approval(self, entra_object_id: str) -> dict | None:
        entra_object_id = self._validate_identity(entra_object_id)

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    entra_object_id,
                    approval_status,
                    reviewed_by,
                    reviewed_at,
                    approval_notes,
                    created_at,
                    updated_at
                FROM dbo.candidate_approvals
                WHERE entra_object_id = ?
                """,
                entra_object_id,
            )
            row = cursor.fetchone()
            return self._serialize(row) if row else None

    def list_approvals(
        self,
        *,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        self._validate_status(status, allow_none=True)
        limit = max(1, min(limit, 500))
        offset = max(0, offset)

        query = """
            SELECT
                a.id,
                a.entra_object_id,
                a.approval_status,
                a.reviewed_by,
                a.reviewed_at,
                a.approval_notes,
                a.created_at,
                a.updated_at,
                c.first_name,
                c.last_name,
                c.email
            FROM dbo.candidate_approvals AS a
            LEFT JOIN dbo.candidates AS c
                ON c.entra_object_id = a.entra_object_id
            WHERE 1 = 1
        """
        parameters: list = []

        if status:
            query += " AND a.approval_status = ?"
            parameters.append(status)

        if search and search.strip():
            pattern = f"%{search.strip()}%"
            query += """
                AND (
                    a.entra_object_id LIKE ?
                    OR ISNULL(c.first_name, N'') LIKE ?
                    OR ISNULL(c.last_name, N'') LIKE ?
                    OR ISNULL(c.email, N'') LIKE ?
                )
            """
            parameters.extend([pattern, pattern, pattern, pattern])

        query += """
            ORDER BY
                CASE WHEN a.approval_status = N'pending' THEN 0 ELSE 1 END,
                a.created_at DESC,
                a.entra_object_id
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        parameters.extend([offset, limit])

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, *parameters)
            return [self._serialize(row) for row in cursor.fetchall()]

    def review_candidate(
        self,
        entra_object_id: str,
        *,
        status: str,
        reviewed_by: str,
        approval_notes: str | None = None,
    ) -> dict | None:
        entra_object_id = self._validate_identity(entra_object_id)
        self._validate_status(status)

        if status == "pending":
            raise ValueError("Review status must be approved or rejected")

        reviewed_by = (reviewed_by or "").strip()
        if not reviewed_by:
            raise ValueError("Reviewer identity is required")

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE dbo.candidate_approvals
                SET
                    approval_status = ?,
                    reviewed_by = ?,
                    reviewed_at = SYSUTCDATETIME(),
                    approval_notes = ?,
                    updated_at = SYSUTCDATETIME()
                OUTPUT
                    INSERTED.id,
                    INSERTED.entra_object_id,
                    INSERTED.approval_status,
                    INSERTED.reviewed_by,
                    INSERTED.reviewed_at,
                    INSERTED.approval_notes,
                    INSERTED.created_at,
                    INSERTED.updated_at
                WHERE entra_object_id = ?
                  AND approval_status = N'pending'
                """,
                status,
                reviewed_by,
                approval_notes,
                entra_object_id,
            )
            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                return None

            result = self._serialize(row)
            connection.commit()
            return result
