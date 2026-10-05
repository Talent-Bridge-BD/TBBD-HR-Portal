from __future__ import annotations

import os
import struct

from azure.identity import AzureCliCredential, DefaultAzureCredential
import pyodbc


class AdministratorNotificationRepository:

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


    def get_email_settings(self):

        with self._connection() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT TOP 1
                    id,
                    provider,
                    sender_address,
                    sender_name,
                    is_active,
                    created_at,
                    updated_at
                FROM dbo.notification_email_settings
                ORDER BY created_at DESC
                """
            )

            row = cursor.fetchone()

            if not row:
                return None

            return {
                "id": str(row.id),
                "provider": row.provider,
                "sender_address": row.sender_address,
                "sender_name": row.sender_name,
                "is_active": bool(row.is_active),
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }


    def list_templates(self):

        with self._connection() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    template_code,
                    name,
                    event_type,
                    subject,
                    is_active,
                    created_at,
                    updated_at
                FROM dbo.notification_templates
                ORDER BY created_at DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": str(row.id),
                    "template_code": row.template_code,
                    "name": row.name,
                    "event_type": row.event_type,
                    "subject": row.subject,
                    "is_active": bool(row.is_active),
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
                for row in rows
            ]


    def list_delivery_logs(self, limit: int = 100):

        with self._connection() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT TOP (?)
                    id,
                    notification_id,
                    recipient,
                    channel,
                    status,
                    error_message,
                    sent_at,
                    created_at
                FROM dbo.notification_delivery_logs
                ORDER BY created_at DESC
                """,
                limit,
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": str(row.id),
                    "notification_id": (
                        str(row.notification_id)
                        if row.notification_id
                        else None
                    ),
                    "recipient": row.recipient,
                    "channel": row.channel,
                    "status": row.status,
                    "error_message": row.error_message,
                    "sent_at": row.sent_at,
                    "created_at": row.created_at,
                }
                for row in rows
            ]

    def create_delivery_log(
        self,
        recipient: str,
        channel: str,
        status: str,
        notification_id=None,
    ):
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.notification_delivery_logs
                (
                    notification_id,
                    recipient,
                    channel,
                    status
                )
                VALUES
                (?, ?, ?, ?)
                """,
                (
                    notification_id,
                    recipient,
                    channel,
                    status,
                ),
            )

            connection.commit()

            return {
                "status": "created",
                "recipient": recipient,
            }
