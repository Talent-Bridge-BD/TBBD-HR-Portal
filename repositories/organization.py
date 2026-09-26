from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod

import pyodbc
from azure.identity import DefaultAzureCredential

from models.organization import Organization, OrganizationMembership


class OrganizationRepository(ABC):

    @abstractmethod
    def get_active_memberships(
        self,
        user_id: str,
    ) -> list[OrganizationMembership]:
        raise NotImplementedError

    @abstractmethod
    def list_active_organizations(self) -> list[Organization]:
        raise NotImplementedError

    @abstractmethod
    def list_members(self, organization_id: str) -> list[OrganizationMembership]:
        raise NotImplementedError

    @abstractmethod
    def add_membership(
        self,
        organization_id: str,
        user_id: str,
        role: str,
    ) -> OrganizationMembership:
        raise NotImplementedError

    @abstractmethod
    def update_membership_status(
        self,
        organization_id: str,
        user_id: str,
        status: str,
        role: str | None = None,
    ) -> OrganizationMembership:
        raise NotImplementedError


class InMemoryOrganizationRepository(OrganizationRepository):

    def __init__(self):
        self._memberships: list[OrganizationMembership] = []
        self._organizations: list[Organization] = []

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

    def list_active_organizations(self) -> list[Organization]:
        return [
            organization
            for organization in self._organizations
            if organization.status == "active"
        ]

    def list_members(self, organization_id: str) -> list[OrganizationMembership]:
        return [
            membership
            for membership in self._memberships
            if membership.organization_id == organization_id
        ]

    def add_membership(
        self,
        organization_id: str,
        user_id: str,
        role: str,
    ) -> OrganizationMembership:
        existing = next(
            (
                membership
                for membership in self._memberships
                if membership.organization_id == organization_id
                and membership.user_id == user_id
            ),
            None,
        )

        if existing is not None:
            raise ValueError("Organization membership already exists")

        membership = OrganizationMembership(
            id=f"membership-{len(self._memberships) + 1:03d}",
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            status="active",
        )
        self._memberships.append(membership)
        return membership

    def update_membership_status(
        self,
        organization_id: str,
        user_id: str,
        status: str,
        role: str | None = None,
    ) -> OrganizationMembership:
        for index, membership in enumerate(self._memberships):
            if (
                membership.organization_id == organization_id
                and membership.user_id == user_id
            ):
                updated = OrganizationMembership(
                    id=membership.id,
                    organization_id=membership.organization_id,
                    user_id=membership.user_id,
                    role=role if role is not None else membership.role,
                    status=status,
                )
                self._memberships[index] = updated
                return updated

        raise ValueError("Organization membership not found")


class SqlOrganizationRepository(OrganizationRepository):
    """
    Azure SQL implementation using Microsoft Entra authentication.

    Reads active organization memberships for an authenticated user
    and active organizations available to authorized system users.
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

    def list_members(self, organization_id: str) -> list[OrganizationMembership]:
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
                WHERE organization_id = ?
                ORDER BY user_id
                """,
                organization_id,
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

    def add_membership(
        self,
        organization_id: str,
        user_id: str,
        role: str,
    ) -> OrganizationMembership:
        import uuid

        membership_id = str(uuid.uuid4())

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO dbo.organization_memberships (
                    id,
                    organization_id,
                    user_id,
                    role,
                    status
                )
                VALUES (?, ?, ?, ?, N'active')
                """,
                membership_id,
                organization_id,
                user_id,
                role,
            )
            connection.commit()

        return OrganizationMembership(
            id=membership_id,
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            status="active",
        )

    def update_membership_status(
        self,
        organization_id: str,
        user_id: str,
        status: str,
        role: str | None = None,
    ) -> OrganizationMembership:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE dbo.organization_memberships
                SET status = ?,
                    role = COALESCE(?, role),
                    updated_at = SYSUTCDATETIME()
                WHERE organization_id = ?
                  AND user_id = ?
                """,
                status,
                role,
                organization_id,
                user_id,
            )

            if cursor.rowcount != 1:
                raise ValueError("Organization membership not found")

            cursor.execute(
                """
                SELECT
                    CONVERT(nvarchar(36), id) AS id,
                    CONVERT(nvarchar(36), organization_id) AS organization_id,
                    user_id,
                    role,
                    status
                FROM dbo.organization_memberships
                WHERE organization_id = ?
                  AND user_id = ?
                """,
                organization_id,
                user_id,
            )

            row = cursor.fetchone()
            connection.commit()

        return OrganizationMembership(
            id=str(row.id),
            organization_id=str(row.organization_id),
            user_id=str(row.user_id),
            role=str(row.role),
            status=str(row.status),
        )

    def list_active_organizations(self) -> list[Organization]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    CONVERT(nvarchar(36), id) AS id,
                    name,
                    status
                FROM dbo.organizations
                WHERE status = N'active'
                ORDER BY name
                """
            )
            rows = cursor.fetchall()

            return [
                Organization(
                    id=str(row.id),
                    name=str(row.name),
                    status=str(row.status),
                )
                for row in rows
            ]
