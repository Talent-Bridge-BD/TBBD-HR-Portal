from __future__ import annotations

import os
import struct

from abc import ABC, abstractmethod

import pyodbc
from azure.identity import DefaultAzureCredential

from models.organization import OrganizationMembership


class OrganizationRepository(ABC):

    @abstractmethod
    def get_active_memberships(
        self,
        user_id: str,
    ) -> list[OrganizationMembership]:
        raise NotImplementedError


class SqlOrganizationRepository(OrganizationRepository):
    """
    Azure SQL implementation using Microsoft Entra authentication.
    The production App Service uses its System Assigned Managed Identity.
    Local development can use DefaultAzureCredential.
    """

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

    def get_active_memberships(
        self,
        user_id: str,
    ) -> list[OrganizationMembership]:
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    user_id,
                    CONVERT(nvarchar(36), organization_id)
                        AS organization_id,
                    role,
                    status
                FROM dbo.organization_memberships
                WHERE user_id = ?
                  AND status = N'active'
                ORDER BY organization_id
                """,
                user_id,
            )

            return [
                OrganizationMembership(
                    user_id=row.user_id,
                    organization_id=row.organization_id,
                    role=row.role,
                    status=row.status,
                )
                for row in cursor.fetchall()
            ]
