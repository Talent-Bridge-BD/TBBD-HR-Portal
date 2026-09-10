import os
import struct
from abc import ABC, abstractmethod

from azure.identity import DefaultAzureCredential

from models.candidate_education import CandidateEducation


class CandidateEducationRepository(ABC):

    @abstractmethod
    def list_education(
        self,
        candidate_id: str,
    ) -> list[CandidateEducation]:
        raise NotImplementedError

    @abstractmethod
    def get_education(
        self,
        candidate_id: str,
        education_id: str,
    ) -> CandidateEducation | None:
        raise NotImplementedError

    @abstractmethod
    def create_education(
        self,
        candidate_id: str,
        degree_qualification: str,
        institution: str,
        field_of_study: str | None,
        start_date,
        end_date,
        description: str | None,
    ) -> CandidateEducation:
        raise NotImplementedError

    @abstractmethod
    def update_education(
        self,
        candidate_id: str,
        education_id: str,
        degree_qualification: str,
        institution: str,
        field_of_study: str | None,
        start_date,
        end_date,
        description: str | None,
    ) -> CandidateEducation | None:
        raise NotImplementedError

    @abstractmethod
    def delete_education(
        self,
        candidate_id: str,
        education_id: str,
    ) -> bool:
        raise NotImplementedError


class SqlCandidateEducationRepository(CandidateEducationRepository):
    """
    Azure SQL implementation using Microsoft Entra authentication.

    Candidate ownership is enforced by joining candidate_education to
    dbo.candidates and matching the authenticated Entra object ID.
    """

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
        self.credential = DefaultAzureCredential()

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
    def _map_row(row) -> CandidateEducation:
        return CandidateEducation(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            degree_qualification=row.degree_qualification,
            institution=row.institution,
            field_of_study=row.field_of_study,
            start_date=row.start_date,
            end_date=row.end_date,
            description=row.description,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_education(
        self,
        candidate_id: str,
    ) -> list[CandidateEducation]:
        sql = """
        SELECT
            e.id,
            e.candidate_id,
            e.degree_qualification,
            e.institution,
            e.field_of_study,
            e.start_date,
            e.end_date,
            e.description,
            e.created_at,
            e.updated_at
        FROM dbo.candidate_education AS e
        INNER JOIN dbo.candidates AS c
            ON c.id = e.candidate_id
        WHERE c.entra_object_id = ?
        ORDER BY
            e.end_date DESC,
            e.start_date DESC,
            e.created_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, candidate_id)
            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_education(
        self,
        candidate_id: str,
        education_id: str,
    ) -> CandidateEducation | None:
        sql = """
        SELECT
            e.id,
            e.candidate_id,
            e.degree_qualification,
            e.institution,
            e.field_of_study,
            e.start_date,
            e.end_date,
            e.description,
            e.created_at,
            e.updated_at
        FROM dbo.candidate_education AS e
        INNER JOIN dbo.candidates AS c
            ON c.id = e.candidate_id
        WHERE e.id = ?
          AND c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                education_id,
                candidate_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def create_education(
        self,
        candidate_id: str,
        degree_qualification: str,
        institution: str,
        field_of_study: str | None,
        start_date,
        end_date,
        description: str | None,
    ) -> CandidateEducation:
        sql = """
        INSERT INTO dbo.candidate_education (
            candidate_id,
            degree_qualification,
            institution,
            field_of_study,
            start_date,
            end_date,
            description
        )
        OUTPUT
            INSERTED.id,
            INSERTED.candidate_id,
            INSERTED.degree_qualification,
            INSERTED.institution,
            INSERTED.field_of_study,
            INSERTED.start_date,
            INSERTED.end_date,
            INSERTED.description,
            INSERTED.created_at,
            INSERTED.updated_at
        SELECT
            c.id,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        FROM dbo.candidates AS c
        WHERE c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                degree_qualification,
                institution,
                field_of_study,
                start_date,
                end_date,
                description,
                candidate_id,
            )
            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError("Candidate profile not found")

            connection.commit()

        return self._map_row(row)

    def update_education(
        self,
        candidate_id: str,
        education_id: str,
        degree_qualification: str,
        institution: str,
        field_of_study: str | None,
        start_date,
        end_date,
        description: str | None,
    ) -> CandidateEducation | None:
        sql = """
        UPDATE e
        SET
            degree_qualification = ?,
            institution = ?,
            field_of_study = ?,
            start_date = ?,
            end_date = ?,
            description = ?,
            updated_at = SYSUTCDATETIME()
        FROM dbo.candidate_education AS e
        INNER JOIN dbo.candidates AS c
            ON c.id = e.candidate_id
        WHERE e.id = ?
          AND c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                degree_qualification,
                institution,
                field_of_study,
                start_date,
                end_date,
                description,
                education_id,
                candidate_id,
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return None

            connection.commit()

        return self.get_education(
            candidate_id,
            education_id,
        )

    def delete_education(
        self,
        candidate_id: str,
        education_id: str,
    ) -> bool:
        sql = """
        DELETE e
        FROM dbo.candidate_education AS e
        INNER JOIN dbo.candidates AS c
            ON c.id = e.candidate_id
        WHERE e.id = ?
          AND c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                education_id,
                candidate_id,
            )

            deleted = cursor.rowcount > 0

            if deleted:
                connection.commit()
            else:
                connection.rollback()

        return deleted
