"""Application-managed roles, separate from approval status and memberships."""
import logging
import os
import struct

import pyodbc
from azure.identity import AzureCliCredential, DefaultAzureCredential


logger = logging.getLogger(__name__)


def _sqlstate(error):
    return next(
        (
            argument
            for argument in getattr(error, "args", ())
            if isinstance(argument, str)
            and len(argument) == 5
            and argument.isascii()
            and argument.isalnum()
        ),
        "unavailable",
    )


class InMemoryApplicationRoleRepository:
    def __init__(self):
        self._roles = {}

    def assignment_status(self, user_id, role):
        return self._roles.get((user_id, role))

    def has_role(self, user_id, role):
        return self._roles.get((user_id, role)) == "active"

    def grant_role(self, user_id, role, assigned_by=None):
        self._roles[(user_id, role)] = "active"
        return True

    def revoke_role(self, user_id, role, assigned_by=None):
        self._roles[(user_id, role)] = "revoked"
        return True


class SqlApplicationRoleRepository:
    SQL_ACCESS_TOKEN_ATTRIBUTE = 1256
    SQL_SCOPE = "https://database.windows.net/.default"

    def __init__(self, server=None, database=None):
        self.server = (
            server
            or os.environ.get("AZURE_SQL_SERVER")
            or os.environ.get("SQL_SERVER")
            or "tbbd-sql-sea.database.windows.net"
        )
        self.database = database or os.environ.get(
            "SQL_DATABASE", "tbbd-hr-db"
        )
        if os.environ.get("WEBSITE_SITE_NAME"):
            self.credential = DefaultAzureCredential()
        else:
            self.credential = AzureCliCredential()

    def _connection(self):
        logger.info(
            "Azure SQL role repository connection target server=%s database=%s credential=%s",
            self.server,
            self.database,
            type(self.credential).__name__,
        )

        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER=tcp:{self.server},1433;"
            f"DATABASE={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        if os.environ.get("WEBSITE_SITE_NAME"):
            try:
                return pyodbc.connect(
                    connection_string + "Authentication=ActiveDirectoryMsi;"
                )
            except pyodbc.Error as error:
                logger.error(
                    "Azure SQL managed identity connection failed; "
                    "exception_type=%s sqlstate=%s",
                    type(error).__name__,
                    _sqlstate(error),
                )
                raise

        try:
            token = self.credential.get_token(self.SQL_SCOPE).token
        except Exception as error:
            logger.error(
                "Azure SQL access token acquisition failed; credential=%s "
                "exception_type=%s",
                type(self.credential).__name__,
                type(error).__name__,
            )
            raise

        logger.info(
            "Azure SQL access token acquired; credential=%s",
            type(self.credential).__name__,
        )
        token_bytes = token.encode("utf-16-le")
        token_struct = struct.pack(
            f"<I{len(token_bytes)}s", len(token_bytes), token_bytes
        )
        try:
            return pyodbc.connect(
                connection_string,
                attrs_before={self.SQL_ACCESS_TOKEN_ATTRIBUTE: token_struct},
            )
        except pyodbc.Error as error:
            logger.error(
                "Azure SQL token-authenticated connection failed; "
                "exception_type=%s sqlstate=%s",
                type(error).__name__,
                _sqlstate(error),
            )
            raise


    def assignment_status(self, user_id, role):
        with self._connection() as connection:
            row = connection.cursor().execute(
                """
                SELECT TOP (1) status
                FROM dbo.application_role_assignments
                WHERE user_id = ? AND role = ?
                """,
                user_id, role,
            ).fetchone()
            return row[0] if row else None

    def has_role(self, user_id, role):
        with self._connection() as connection:
            row = connection.cursor().execute(
                """
                SELECT TOP (1) 1
                FROM dbo.application_role_assignments
                WHERE user_id = ? AND role = ? AND status = N'active'
                """,
                user_id, role,
            ).fetchone()
            return row is not None

    def grant_role(self, user_id, role, assigned_by=None):
        with self._connection() as connection:
            connection.cursor().execute(
                """
                IF EXISTS (
                    SELECT 1 FROM dbo.application_role_assignments
                        WITH (UPDLOCK, HOLDLOCK)
                    WHERE user_id = ? AND role = ?
                )
                    UPDATE dbo.application_role_assignments
                    SET status = N'active', assigned_by = ?,
                        updated_at = SYSUTCDATETIME()
                    WHERE user_id = ? AND role = ?
                ELSE
                    INSERT INTO dbo.application_role_assignments
                        (user_id, role, status, assigned_by)
                    VALUES (?, ?, N'active', ?)
                """,
                user_id, role, assigned_by,
                user_id, role,
                user_id, role, assigned_by,
            )
            connection.commit()
        return True

    def revoke_role(self, user_id, role, assigned_by=None):
        with self._connection() as connection:
            connection.cursor().execute(
                """
                UPDATE dbo.application_role_assignments
                SET status = N'revoked', assigned_by = ?,
                    updated_at = SYSUTCDATETIME()
                WHERE user_id = ? AND role = ?
                """,
                assigned_by, user_id, role,
            )
            connection.commit()
        return True


application_role_repository = SqlApplicationRoleRepository()
