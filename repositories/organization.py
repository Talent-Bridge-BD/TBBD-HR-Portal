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


class InMemoryOrganizationRepository(OrganizationRepository):
    def __init__(self):
        self._memberships: list[OrganizationMembership] = []

    def get_active_memberships(
        self,
        user_id: str,
    ) -> list[OrganizationMembership]:
        return [
            membership
            for membership in self._memberships
            if membership.user_id == user_id
            and membership.status == "active"
        ]


class SqlOrganizationRepository(OrganizationRepository):
    """
    Azure SQL implementation using Microsoft Entra authentication.

    Reads active organization memberships for an authenticated user.
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
                    CONVERT(nvarchar(36), id) AS id,
                    CONVERT(nvarchar(36), organization_id) AS organization_id,
                    user_id,
                    role,
                    status
                FROM dbo.organization_memberships
                WHERE user_id = ?
                  AND status = N'active'
                ORDER BY organization_id
                """,
                user_id,
            )

            rows = cursor.fetchall()

            return [
                OrganizationMembership(
                    id=str(row.id),
                    organization_id=str(row.organization_id),
                    user_id=str(row.user_id),
                    role=str(row.role),
                    status=str(row.status),
                )
                for row in rows
            ]
