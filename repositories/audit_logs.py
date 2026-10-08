from __future__ import annotations

import json
import os
import struct

from azure.identity import AzureCliCredential, DefaultAzureCredential
import pyodbc


class AuditLogRepository:

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

    def create_log(
        self,
        *,
        user_id: str | None,
        user_email: str | None,
        user_name: str | None,
        organization_id: str | None,
        event_type: str,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        status: str = "success",
        details: dict | list | str | None = None,
    ) -> str:

        if status not in {"success", "failure"}:
            raise ValueError("status must be 'success' or 'failure'")

        if isinstance(details, (dict, list)):
            details_value = json.dumps(
                details,
                ensure_ascii=False,
                default=str,
            )
        else:
            details_value = details

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.audit_logs (
                    user_id,
                    user_email,
                    user_name,
                    organization_id,
                    event_type,
                    action,
                    entity_type,
                    entity_id,
                    status,
                    details
                )
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                user_id,
                user_email,
                user_name,
                organization_id,
                event_type,
                action,
                entity_type,
                entity_id,
                status,
                details_value,
            )

            row = cursor.fetchone()
            connection.commit()

            return str(row.id)

    def list_recent(self, limit: int = 100):

        limit = max(1, min(limit, 500))

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT TOP (?)
                    id,
                    user_id,
                    user_email,
                    user_name,
                    organization_id,
                    event_type,
                    action,
                    entity_type,
                    entity_id,
                    status,
                    details,
                    created_at
                FROM dbo.audit_logs
                ORDER BY created_at DESC
                """,
                limit,
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": str(row.id),
                    "user_id": row.user_id,
                    "user_email": row.user_email,
                    "user_name": row.user_name,
                    "organization_id": (
                        str(row.organization_id)
                        if row.organization_id
                        else None
                    ),
                    "event_type": row.event_type,
                    "action": row.action,
                    "entity_type": row.entity_type,
                    "entity_id": row.entity_id,
                    "status": row.status,
                    "details": row.details,
                    "created_at": row.created_at,
                }
                for row in rows
            ]

    def list_recent_for_organizations(
        self,
        organization_ids: set[str],
        limit: int = 3,
    ):
        limit = max(1, min(limit, 50))

        if not organization_ids:
            return []

        placeholders = ", ".join("?" for _ in organization_ids)

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                f"""
                SELECT TOP (?)
                    id,
                    user_id,
                    user_email,
                    user_name,
                    organization_id,
                    event_type,
                    action,
                    entity_type,
                    entity_id,
                    status,
                    details,
                    created_at
                FROM dbo.audit_logs
                WHERE organization_id IN ({placeholders})
                ORDER BY created_at DESC
                """,
                limit,
                *organization_ids,
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": str(row.id),
                    "user_id": row.user_id,
                    "user_email": row.user_email,
                    "user_name": row.user_name,
                    "organization_id": (
                        str(row.organization_id)
                        if row.organization_id
                        else None
                    ),
                    "event_type": row.event_type,
                    "action": row.action,
                    "entity_type": row.entity_type,
                    "entity_id": row.entity_id,
                    "status": row.status,
                    "details": row.details,
                    "created_at": row.created_at,
                }
                for row in rows
            ]

    def count_recent_failures(self) -> int:

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.audit_logs
                WHERE status = 'failure'
                """
            )

            return int(cursor.fetchone()[0])
