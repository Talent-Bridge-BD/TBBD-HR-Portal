from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.user_profile import UserProfile


class UserProfileRepository(ABC):
    @abstractmethod
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        raise NotImplementedError

    @abstractmethod
    def save_profile(self, profile: UserProfile) -> UserProfile:
        raise NotImplementedError


class SqlUserProfileRepository(UserProfileRepository):
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
    def _row_to_profile(row: pyodbc.Row) -> UserProfile:
        return UserProfile(
            user_id=str(row.user_id),
            full_name=row.full_name or "",
            primary_email=row.primary_email or "",
            phone=row.phone or "",
            office_phone=row.office_phone or "",
            organization_email=row.organization_email or "",
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    user_id,
                    full_name,
                    primary_email,
                    phone,
                    office_phone,
                    organization_email,
                    created_at,
                    updated_at
                FROM dbo.user_profiles
                WHERE user_id = ?
                """,
                user_id,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_profile(row)

    def save_profile(self, profile: UserProfile) -> UserProfile:
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT user_id
                FROM dbo.user_profiles
                WHERE user_id = ?
                """,
                profile.user_id,
            )
            existing = cursor.fetchone()

            if existing is None:
                cursor.execute(
                    """
                    INSERT INTO dbo.user_profiles (
                        user_id,
                        full_name,
                        primary_email,
                        phone,
                        office_phone,
                        organization_email
                    )
                    OUTPUT
                        INSERTED.user_id,
                        INSERTED.full_name,
                        INSERTED.primary_email,
                        INSERTED.phone,
                        INSERTED.office_phone,
                        INSERTED.organization_email,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    profile.user_id,
                    profile.full_name,
                    profile.primary_email,
                    profile.phone,
                    profile.office_phone,
                    profile.organization_email,
                )
            else:
                cursor.execute(
                    """
                    UPDATE dbo.user_profiles
                    SET
                        full_name = ?,
                        primary_email = ?,
                        phone = ?,
                        office_phone = ?,
                        organization_email = ?,
                        updated_at = SYSUTCDATETIME()
                    OUTPUT
                        INSERTED.user_id,
                        INSERTED.full_name,
                        INSERTED.primary_email,
                        INSERTED.phone,
                        INSERTED.office_phone,
                        INSERTED.organization_email,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    WHERE user_id = ?
                    """,
                    profile.full_name,
                    profile.primary_email,
                    profile.phone,
                    profile.office_phone,
                    profile.organization_email,
                    profile.user_id,
                )

            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("Failed to save user profile")

            connection.commit()
            return self._row_to_profile(row)
