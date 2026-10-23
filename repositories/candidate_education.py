import os
import struct

import pyodbc
from azure.identity import AzureCliCredential


class SqlCandidateEducationRepository:
    """Candidate Education access using the deployed SQL schema."""

    SQL_SCOPE = "https://database.windows.net/.default"
    SQL_ACCESS_TOKEN_ATTRIBUTE = 1256

    def __init__(
        self,
        server: str | None = None,
        database: str | None = None,
    ):
        self.server = (
            server
            or os.environ.get("AZURE_SQL_SERVER")
            or os.environ.get("SQL_SERVER")
            or "tbbd-sql-sea.database.windows.net"
        )
        self.database = (
            database
            or os.environ.get("SQL_DATABASE")
            or "tbbd-hr-db"
        )
        self.credential = (
            None
            if os.environ.get("WEBSITE_SITE_NAME")
            else AzureCliCredential()
        )

    def _connection(self) -> pyodbc.Connection:
        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER=tcp:{self.server},1433;"
            f"DATABASE={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        # In Azure App Service, ODBC obtains the managed identity token.
        if os.environ.get("WEBSITE_SITE_NAME"):
            return pyodbc.connect(
                connection_string + "Authentication=ActiveDirectoryMsi;"
            )

        # Preserve Azure CLI token authentication for local development.
        if self.credential is None:
            self.credential = AzureCliCredential()

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
    def _validate_identity(identity: str) -> str:
        value = (identity or "").strip()
        if not value:
            raise ValueError("Candidate identity is required.")
        if len(value) > 100:
            raise ValueError("Candidate identity is too long.")
        return value

    @staticmethod
    def _optional_text(
        value,
        field_name: str,
        max_length: int,
    ) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        if not text:
            return None
        if len(text) > max_length:
            raise ValueError(
                f"{field_name} cannot exceed {max_length} characters."
            )
        return text

    @staticmethod
    def _passing_year(value) -> int | None:
        if value is None or not str(value).strip():
            return None

        try:
            year = int(str(value).strip())
        except (TypeError, ValueError) as exc:
            raise ValueError("Passing year must be a whole number.") from exc

        if not 1950 <= year <= 2100:
            raise ValueError("Passing year must be between 1950 and 2100.")

        return year

    @staticmethod
    def _serialize(row) -> dict:
        # Translate the live SQL column names into the existing API contract.
        return {
            "highest_education": row.degree_qualification,
            "institution_name": row.institution,
            "field_of_study": row.field_of_study,
            "passing_year": row.passing_year,
            "gpa_result": row.result_gpa,
        }

    def get_education(self, candidate_identity: str) -> dict | None:
        """Return the most recently updated Education record for this candidate."""
        identity = self._validate_identity(candidate_identity)

        sql = """
            SELECT TOP (1)
                e.degree_qualification,
                e.institution,
                e.field_of_study,
                e.passing_year,
                e.result_gpa
            FROM dbo.candidate_education AS e
            INNER JOIN dbo.candidates AS c
                ON c.id = e.candidate_id
            WHERE c.entra_object_id = ?
            ORDER BY
                e.updated_at DESC,
                e.created_at DESC,
                e.id DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, identity)
            row = cursor.fetchone()

        return self._serialize(row) if row is not None else None

    def save_education(
        self,
        candidate_identity: str,
        payload: dict,
    ) -> dict:
        """Create or update the latest Education record for this candidate."""
        identity = self._validate_identity(candidate_identity)

        if not isinstance(payload, dict):
            raise ValueError("Education payload must be an object.")

        degree = self._optional_text(
            payload.get("highest_education"),
            "Highest education",
            200,
        )
        institution = self._optional_text(
            payload.get("institution_name"),
            "Institution name",
            250,
        )
        field = self._optional_text(
            payload.get("field_of_study"),
            "Field of study",
            200,
        )
        year = self._passing_year(payload.get("passing_year"))
        result = self._optional_text(
            payload.get("gpa_result"),
            "GPA/result",
            100,
        )

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id
                FROM dbo.candidates
                WHERE entra_object_id = ?;
                """,
                identity,
            )
            candidate = cursor.fetchone()

            if candidate is None:
                connection.rollback()
                raise ValueError("Candidate profile not found.")

            candidate_id = candidate.id

            cursor.execute(
                """
                SELECT TOP (1) id
                FROM dbo.candidate_education WITH (UPDLOCK, HOLDLOCK)
                WHERE candidate_id = ?
                ORDER BY updated_at DESC, created_at DESC, id DESC;
                """,
                candidate_id,
            )
            existing = cursor.fetchone()

            if existing is not None:
                cursor.execute(
                    """
                    UPDATE dbo.candidate_education
                    SET
                        degree_qualification = ?,
                        institution = ?,
                        field_of_study = ?,
                        passing_year = ?,
                        result_gpa = ?,
                        updated_at = SYSUTCDATETIME()
                    OUTPUT
                        INSERTED.degree_qualification,
                        INSERTED.institution,
                        INSERTED.field_of_study,
                        INSERTED.passing_year,
                        INSERTED.result_gpa
                    WHERE id = ?
                      AND candidate_id = ?;
                    """,
                    degree,
                    institution,
                    field,
                    year,
                    result,
                    existing.id,
                    candidate_id,
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO dbo.candidate_education (
                        candidate_id,
                        degree_qualification,
                        institution,
                        field_of_study,
                        passing_year,
                        result_gpa
                    )
                    OUTPUT
                        INSERTED.degree_qualification,
                        INSERTED.institution,
                        INSERTED.field_of_study,
                        INSERTED.passing_year,
                        INSERTED.result_gpa
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    candidate_id,
                    degree,
                    institution,
                    field,
                    year,
                    result,
                )

            saved = cursor.fetchone()
            if saved is None:
                connection.rollback()
                raise RuntimeError("Education record could not be saved.")

            result_payload = self._serialize(saved)
            connection.commit()

        return result_payload