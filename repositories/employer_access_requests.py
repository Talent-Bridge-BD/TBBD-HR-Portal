from __future__ import annotations

import os
import struct
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import pyodbc
from azure.identity import AzureCliCredential, DefaultAzureCredential


class EmployerAccessRequestRepository(ABC):
    @abstractmethod
    def create_request(self, payload: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_requests(
        self,
        *,
        status: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def review_request(
        self,
        request_id: str,
        *,
        status: str,
        reviewed_by: str,
        review_notes: str | None = None,
    ) -> dict | None:
        raise NotImplementedError


class InMemoryEmployerAccessRequestRepository(
    EmployerAccessRequestRepository
):
    ALLOWED_STATUSES = {"pending", "approved", "rejected"}

    def __init__(self):
        self._requests: list[dict] = []

    @staticmethod
    def _clean_payload(payload: dict) -> dict:
        required_fields = {
            "company_name": 200,
            "representative_name": 200,
            "email": 320,
        }
        optional_fields = {
            "phone": 50,
            "country": 100,
            "industry": 150,
            "requested_roles": 1000,
            "requirements": 10000,
        }
        cleaned = {}

        for field, maximum in required_fields.items():
            value = str(payload.get(field) or "").strip()
            if not value:
                raise ValueError(f"{field} is required")
            if len(value) > maximum:
                raise ValueError(f"{field} exceeds {maximum} characters")
            cleaned[field] = value

        for field, maximum in optional_fields.items():
            value = str(payload.get(field) or "").strip() or None
            if value is not None and len(value) > maximum:
                raise ValueError(f"{field} exceeds {maximum} characters")
            cleaned[field] = value

        cleaned["email"] = cleaned["email"].casefold()
        return cleaned

    def create_request(self, payload: dict) -> dict:
        cleaned = self._clean_payload(payload)

        for existing in self._requests:
            if (
                existing["status"] == "pending"
                and existing["email"] == cleaned["email"]
                and existing["company_name"].casefold()
                == cleaned["company_name"].casefold()
            ):
                raise ValueError(
                    "A pending request already exists for this email and organization"
                )

        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": str(uuid.uuid4()),
            **cleaned,
            "status": "pending",
            "reviewed_by": None,
            "reviewed_at": None,
            "review_notes": None,
            "created_at": now,
            "updated_at": now,
        }
        self._requests.append(item)
        return dict(item)

    def list_requests(
        self,
        *,
        status: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> list[dict]:
        if status is not None and status not in self.ALLOWED_STATUSES:
            raise ValueError("Invalid request status")

        rows = [
            item for item in self._requests
            if status is None or item["status"] == status
        ]
        rows.sort(key=lambda item: item["created_at"], reverse=True)
        return [dict(item) for item in rows[offset:offset + limit]]

    def review_request(
        self,
        request_id: str,
        *,
        status: str,
        reviewed_by: str,
        review_notes: str | None = None,
    ) -> dict | None:
        if status not in {"approved", "rejected"}:
            raise ValueError("Review status must be approved or rejected")

        reviewer = (reviewed_by or "").strip()
        if not reviewer:
            raise ValueError("Reviewer identity is required")

        notes = (review_notes or "").strip() or None
        if notes and len(notes) > 2000:
            raise ValueError("Review notes exceed 2000 characters")

        item = next(
            (row for row in self._requests if row["id"] == request_id),
            None,
        )
        if item is None or item["status"] != "pending":
            return None

        now = datetime.now(timezone.utc).isoformat()
        item.update({
            "status": status,
            "reviewed_by": reviewer,
            "reviewed_at": now,
            "review_notes": notes,
            "updated_at": now,
        })
        return dict(item)


class SqlEmployerAccessRequestRepository(
    EmployerAccessRequestRepository
):
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
                if row.reviewed_at else None
            ),
            "review_notes": row.review_notes,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }

    def create_request(self, payload: dict) -> dict:
        cleaned = InMemoryEmployerAccessRequestRepository._clean_payload(
            payload
        )
        request_id = str(uuid.uuid4())

        try:
            with self._connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    SELECT TOP 1 id
                    FROM dbo.employer_access_requests
                    WHERE status = N'pending'
                      AND LOWER(email) = ?
                      AND LOWER(company_name) = ?
                    """,
                    cleaned["email"],
                    cleaned["company_name"].casefold(),
                )
                if cursor.fetchone():
                    raise ValueError(
                        "A pending request already exists for this email and organization"
                    )

                cursor.execute(
                    """
                    INSERT INTO dbo.employer_access_requests (
                        id, company_name, representative_name, email,
                        phone, country, industry, requested_roles, requirements,
                        status, created_at, updated_at
                    )
                    OUTPUT
                        INSERTED.id, INSERTED.company_name,
                        INSERTED.representative_name, INSERTED.email,
                        INSERTED.phone, INSERTED.country, INSERTED.industry,
                        INSERTED.requested_roles, INSERTED.requirements,
                        INSERTED.status, INSERTED.reviewed_by,
                        INSERTED.reviewed_at, INSERTED.review_notes,
                        INSERTED.created_at, INSERTED.updated_at
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, N'pending',
                        SYSUTCDATETIME(), SYSUTCDATETIME()
                    )
                    """,
                    request_id,
                    cleaned["company_name"],
                    cleaned["representative_name"],
                    cleaned["email"],
                    cleaned["phone"],
                    cleaned["country"],
                    cleaned["industry"],
                    cleaned["requested_roles"],
                    cleaned["requirements"],
                )
                row = cursor.fetchone()
                if row is None:
                    raise RuntimeError("Request could not be created")
                result = self._serialize(row)
                connection.commit()
                return result
        except pyodbc.IntegrityError as exc:
            raise ValueError(
                "A duplicate request could not be accepted"
            ) from exc

    def list_requests(
        self,
        *,
        status: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> list[dict]:
        if status is not None and status not in self.ALLOWED_STATUSES:
            raise ValueError("Invalid request status")

        query = """
            SELECT
                id, company_name, representative_name, email,
                phone, country, industry, requested_roles, requirements,
                status, reviewed_by, reviewed_at, review_notes,
                created_at, updated_at
            FROM dbo.employer_access_requests
        """
        parameters = []
        if status:
            query += " WHERE status = ?"
            parameters.append(status)
        query += " ORDER BY created_at DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        parameters.extend([offset, limit])

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, *parameters)
            return [self._serialize(row) for row in cursor.fetchall()]

    def review_request(
        self,
        request_id: str,
        *,
        status: str,
        reviewed_by: str,
        review_notes: str | None = None,
    ) -> dict | None:
        if status not in {"approved", "rejected"}:
            raise ValueError("Review status must be approved or rejected")

        reviewer = (reviewed_by or "").strip()
        if not reviewer:
            raise ValueError("Reviewer identity is required")

        notes = (review_notes or "").strip() or None
        if notes and len(notes) > 2000:
            raise ValueError("Review notes exceed 2000 characters")

        try:
            parsed_id = str(uuid.UUID(request_id))
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError("Invalid request ID") from exc

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE dbo.employer_access_requests
                SET status = ?, reviewed_by = ?, reviewed_at = SYSUTCDATETIME(),
                    review_notes = ?, updated_at = SYSUTCDATETIME()
                OUTPUT
                    INSERTED.id, INSERTED.company_name,
                    INSERTED.representative_name, INSERTED.email,
                    INSERTED.phone, INSERTED.country, INSERTED.industry,
                    INSERTED.requested_roles, INSERTED.requirements,
                    INSERTED.status, INSERTED.reviewed_by,
                    INSERTED.reviewed_at, INSERTED.review_notes,
                    INSERTED.created_at, INSERTED.updated_at
                WHERE id = ? AND status = N'pending'
                """,
                status,
                reviewer,
                notes,
                parsed_id,
            )
            row = cursor.fetchone()
            if row is None:
                connection.rollback()
                return None
            result = self._serialize(row)
            connection.commit()
            return result
