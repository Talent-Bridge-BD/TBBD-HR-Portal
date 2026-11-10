from __future__ import annotations

import os
import struct

from azure.identity import AzureCliCredential, DefaultAzureCredential


class SqlCandidateEducationRepository:
    """Read and save one Education form record for the authenticated candidate."""

    SQL_SCOPE = "https://database.windows.net/.default"
    SQL_ACCESS_TOKEN_ATTRIBUTE = 1256

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
        import pyodbc

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
    def _map_row(row) -> dict:
        return {
            "highest_education": row.degree_qualification or "",
            "institution_name": row.institution or "",
            "field_of_study": row.field_of_study or "",
            "passing_year": (
                str(row.passing_year)
                if row.passing_year is not None
                else ""
            ),
            "gpa_result": row.result_gpa or "",
        }

    def get_education(self, user_id: str) -> dict:
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
        ORDER BY e.updated_at DESC, e.created_at DESC;
        """
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, user_id)
            row = cursor.fetchone()

        if row is None:
            return self.empty_education()

        return self._map_row(row)

    def save_education(self, user_id: str, education: dict) -> dict:
        highest_education = self._clean(education.get("highest_education"))
        institution = self._clean(education.get("institution_name"))
        field_of_study = self._clean(education.get("field_of_study"))
        passing_year = self._clean(education.get("passing_year"))
        result_gpa = self._clean(education.get("gpa_result"))

        if passing_year:
            try:
                year = int(passing_year)
            except (TypeError, ValueError) as exc:
                raise ValueError("Passing year must be a valid year.") from exc
            if year < 1950 or year > 2100:
                raise ValueError("Passing year must be between 1950 and 2100.")
        else:
            year = None

        values = (
            highest_education or None,
            institution or None,
            field_of_study or None,
            year,
            result_gpa or None,
        )

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT TOP (1) e.id
                FROM dbo.candidate_education AS e
                INNER JOIN dbo.candidates AS c
                    ON c.id = e.candidate_id
                WHERE c.entra_object_id = ?
                ORDER BY e.updated_at DESC, e.created_at DESC;
                """,
                user_id,
            )
            existing = cursor.fetchone()

            if existing is not None:
                cursor.execute(
                    """
                    UPDATE dbo.candidate_education
                    SET degree_qualification = ?,
                        institution = ?,
                        field_of_study = ?,
                        passing_year = ?,
                        result_gpa = ?,
                        updated_at = SYSUTCDATETIME()
                    WHERE id = ?;
                    """,
                    *values,
                    existing.id,
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO dbo.candidate_education
                        (candidate_id, degree_qualification, institution,
                         field_of_study, passing_year, result_gpa,
                         created_at, updated_at)
                    SELECT
                        c.id, ?, ?, ?, ?, ?,
                        SYSUTCDATETIME(), SYSUTCDATETIME()
                    FROM dbo.candidates AS c
                    WHERE c.entra_object_id = ?;
                    """,
                    *values,
                    user_id,
                )
                if cursor.rowcount == 0:
                    raise ValueError(
                        "Candidate record was not found. Save the candidate "
                        "profile before saving Education."
                    )

            connection.commit()

        return {
            "highest_education": highest_education,
            "institution_name": institution,
            "field_of_study": field_of_study,
            "passing_year": str(year) if year is not None else "",
            "gpa_result": result_gpa,
        }

    @staticmethod
    def _clean(value) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def empty_education() -> dict:
        return {
            "highest_education": "",
            "institution_name": "",
            "field_of_study": "",
            "passing_year": "",
            "gpa_result": "",
        }


class InMemoryCandidateEducationRepository:
    """Test-only Education store; does not connect to SQL."""

    def __init__(self):
        self._education: dict[str, dict] = {}

    @staticmethod
    def empty_education() -> dict:
        return {
            "highest_education": "",
            "institution_name": "",
            "field_of_study": "",
            "passing_year": "",
            "gpa_result": "",
        }

    def get_education(self, user_id: str) -> dict:
        return dict(self._education.get(user_id, self.empty_education()))

    def save_education(self, user_id: str, education: dict) -> dict:
        values = self.empty_education()
        for key in values:
            value = education.get(key)
            values[key] = "" if value is None else str(value).strip()

        year = values["passing_year"]
        if year:
            try:
                year_number = int(year)
            except ValueError as exc:
                raise ValueError("Passing year must be a valid year.") from exc
            if year_number < 1950 or year_number > 2100:
                raise ValueError("Passing year must be between 1950 and 2100.")
            values["passing_year"] = str(year_number)

        self._education[user_id] = values
        return dict(values)
