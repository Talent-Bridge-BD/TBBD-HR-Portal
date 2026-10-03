from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import AzureCliCredential, DefaultAzureCredential


class NotificationRepository(ABC):

    @abstractmethod
    def list_for_recipient(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
        limit: int = 50,
    ) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def count_unread(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    def mark_read(
        self,
        notification_id: str,
        recipient_user_id: str,
    ) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def mark_all_read(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        *,
        candidate_id: str,
        recipient_user_id: str,
        recipient_type: str,
        title: str,
        message: str,
        notification_type: str,
        event_type: str,
        organization_id: str | None = None,
        application_id: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> dict:
        raise NotImplementedError


class SqlNotificationRepository(NotificationRepository):

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
    def _row_to_dict(row) -> dict:
        return {
            "id": str(row.id),
            "candidate_id": str(row.candidate_id),
            "recipient_user_id": row.recipient_user_id,
            "recipient_type": row.recipient_type,
            "organization_id": (
                str(row.organization_id)
                if row.organization_id is not None
                else None
            ),
            "application_id": (
                str(row.application_id)
                if row.application_id is not None
                else None
            ),
            "type": row.type,
            "event_type": row.event_type,
            "title": row.title,
            "message": row.message,
            "is_read": bool(row.is_read),
            "related_entity_type": row.related_entity_type,
            "related_entity_id": (
                str(row.related_entity_id)
                if row.related_entity_id is not None
                else None
            ),
            "created_at": row.created_at,
            "read_at": row.read_at,
        }

    @staticmethod
    def _notification_select() -> str:
        return """
            SELECT
                n.id,
                n.candidate_id,
                n.recipient_user_id,
                n.recipient_type,
                n.organization_id,
                n.application_id,
                n.type,
                n.event_type,
                n.title,
                n.message,
                n.is_read,
                n.related_entity_type,
                n.related_entity_id,
                n.created_at,
                n.read_at
            FROM dbo.notifications AS n
        """

    def list_for_recipient(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
        limit: int = 50,
    ) -> list[dict]:

        safe_limit = max(1, min(limit, 100))

        sql = (
            self._notification_select()
            + """
            WHERE n.recipient_user_id = ?
            """
        )

        parameters: list[object] = [
            recipient_user_id,
        ]

        if organization_ids is not None:
            if not organization_ids:
                return []

            placeholders = ", ".join(
                "?" for _ in organization_ids
            )

            sql += f"""
                AND (
                    n.organization_id IS NULL
                    OR n.organization_id IN ({placeholders})
                )
            """

            parameters.extend(sorted(organization_ids))

        sql += f"""
            ORDER BY n.created_at DESC
            OFFSET 0 ROWS
            FETCH NEXT {safe_limit} ROWS ONLY;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, *parameters)
            rows = cursor.fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    def count_unread(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
    ) -> int:

        sql = """
            SELECT COUNT_BIG(*)
            FROM dbo.notifications AS n
            WHERE n.recipient_user_id = ?
              AND n.is_read = 0
        """

        parameters: list[object] = [
            recipient_user_id,
        ]

        if organization_ids is not None:
            if not organization_ids:
                return 0

            placeholders = ", ".join(
                "?" for _ in organization_ids
            )

            sql += f"""
                AND (
                    n.organization_id IS NULL
                    OR n.organization_id IN ({placeholders})
                )
            """

            parameters.extend(sorted(organization_ids))

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, *parameters)
            row = cursor.fetchone()

        return int(row[0]) if row else 0

    def mark_read(
        self,
        notification_id: str,
        recipient_user_id: str,
    ) -> Optional[dict]:

        sql = """
            UPDATE dbo.notifications
            SET
                is_read = 1,
                read_at = COALESCE(
                    read_at,
                    SYSUTCDATETIME()
                )
            OUTPUT
                INSERTED.id,
                INSERTED.candidate_id,
                INSERTED.recipient_user_id,
                INSERTED.recipient_type,
                INSERTED.organization_id,
                INSERTED.application_id,
                INSERTED.type,
                INSERTED.event_type,
                INSERTED.title,
                INSERTED.message,
                INSERTED.is_read,
                INSERTED.related_entity_type,
                INSERTED.related_entity_id,
                INSERTED.created_at,
                INSERTED.read_at
            WHERE id = ?
              AND recipient_user_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                notification_id,
                recipient_user_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                return None

            connection.commit()

        return self._row_to_dict(row)

    def mark_all_read(
        self,
        recipient_user_id: str,
        organization_ids: set[str] | None = None,
    ) -> int:

        sql = """
            UPDATE dbo.notifications
            SET
                is_read = 1,
                read_at = COALESCE(
                    read_at,
                    SYSUTCDATETIME()
                )
            WHERE recipient_user_id = ?
              AND is_read = 0
        """

        parameters: list[object] = [
            recipient_user_id,
        ]

        if organization_ids is not None:
            if not organization_ids:
                return 0

            placeholders = ", ".join(
                "?" for _ in organization_ids
            )

            sql += f"""
                AND (
                    organization_id IS NULL
                    OR organization_id IN ({placeholders})
                )
            """

            parameters.extend(sorted(organization_ids))

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, *parameters)

            affected = cursor.rowcount

            connection.commit()

        return max(affected, 0)

    def create(
        self,
        *,
        candidate_id: str,
        recipient_user_id: str,
        recipient_type: str,
        title: str,
        message: str,
        notification_type: str,
        event_type: str,
        organization_id: str | None = None,
        application_id: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> dict:

        sql = """
            INSERT INTO dbo.notifications (
                candidate_id,
                recipient_user_id,
                recipient_type,
                organization_id,
                application_id,
                type,
                event_type,
                title,
                message,
                related_entity_type,
                related_entity_id
            )
            OUTPUT
                INSERTED.id,
                INSERTED.candidate_id,
                INSERTED.recipient_user_id,
                INSERTED.recipient_type,
                INSERTED.organization_id,
                INSERTED.application_id,
                INSERTED.type,
                INSERTED.event_type,
                INSERTED.title,
                INSERTED.message,
                INSERTED.is_read,
                INSERTED.related_entity_type,
                INSERTED.related_entity_id,
                INSERTED.created_at,
                INSERTED.read_at
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            );
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                candidate_id,
                recipient_user_id,
                recipient_type,
                organization_id,
                application_id,
                notification_type,
                event_type,
                title,
                message,
                related_entity_type,
                related_entity_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise RuntimeError(
                    "Notification could not be created"
                )

            connection.commit()

        return self._row_to_dict(row)
