from abc import ABC, abstractmethod
import struct

from azure.identity import DefaultAzureCredential

from models.interview import EmployerInterview


class InterviewRepository(ABC):

    @abstractmethod
    def list_interviews(
        self,
        organization_id: str,
    ) -> list[EmployerInterview]:
        raise NotImplementedError

    @abstractmethod
    def get_interview(
        self,
        organization_id: str,
        interview_id: str,
    ) -> EmployerInterview | None:
        raise NotImplementedError

    @abstractmethod
    def create_interview(
        self,
        organization_id: str,
        application_id: str,
        scheduled_start,
        scheduled_end,
        interview_type: str,
        location_or_link: str,
        interviewer_name: str,
        notes: str,
    ) -> EmployerInterview:
        raise NotImplementedError

    @abstractmethod
    def update_interview(
        self,
        organization_id: str,
        interview_id: str,
        scheduled_start,
        scheduled_end,
        interview_type: str,
        location_or_link: str,
        interviewer_name: str,
        notes: str,
        status: str,
    ) -> EmployerInterview | None:
        raise NotImplementedError


class SqlInterviewRepository(InterviewRepository):

    SQL_SCOPE = "https://database.windows.net/.default"
    SQL_ACCESS_TOKEN_ATTRIBUTE = 1256

    def __init__(self):
        self.server = "tbbd-sql-sea.database.windows.net"
        self.database = "tbbd-hr-db"
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
    def _map_row(row) -> EmployerInterview:
        return EmployerInterview(
            id=str(row.id),
            application_id=str(row.application_id),
            candidate_id=str(row.candidate_id),
            job_id=str(row.job_id),
            candidate_first_name=row.first_name,
            candidate_last_name=row.last_name,
            candidate_email=row.email,
            job_title=row.job_title,
            scheduled_start=row.scheduled_start,
            scheduled_end=row.scheduled_end,
            interview_type=row.interview_type,
            location_or_link=row.location_or_link,
            interviewer_name=row.interviewer_name,
            notes=row.notes,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_interviews(
        self,
        organization_id: str,
    ) -> list[EmployerInterview]:

        sql = """
        SELECT
            i.id,
            i.application_id,
            a.candidate_id,
            a.job_id,
            c.first_name,
            c.last_name,
            c.email,
            j.title AS job_title,
            i.scheduled_start,
            i.scheduled_end,
            i.interview_type,
            i.location_or_link,
            i.interviewer_name,
            i.notes,
            i.status,
            i.created_at,
            i.updated_at
        FROM dbo.interviews AS i
        INNER JOIN dbo.applications AS a
            ON a.id = i.application_id
        INNER JOIN dbo.candidates AS c
            ON c.id = a.candidate_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE j.organization_id = ?
        ORDER BY i.scheduled_start ASC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, organization_id)
            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_interview(
        self,
        organization_id: str,
        interview_id: str,
    ) -> EmployerInterview | None:

        sql = """
        SELECT
            i.id,
            i.application_id,
            a.candidate_id,
            a.job_id,
            c.first_name,
            c.last_name,
            c.email,
            j.title AS job_title,
            i.scheduled_start,
            i.scheduled_end,
            i.interview_type,
            i.location_or_link,
            i.interviewer_name,
            i.notes,
            i.status,
            i.created_at,
            i.updated_at
        FROM dbo.interviews AS i
        INNER JOIN dbo.applications AS a
            ON a.id = i.application_id
        INNER JOIN dbo.candidates AS c
            ON c.id = a.candidate_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE i.id = ?
          AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                interview_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def create_interview(
        self,
        organization_id: str,
        application_id: str,
        scheduled_start,
        scheduled_end,
        interview_type: str,
        location_or_link: str,
        interviewer_name: str,
        notes: str,
    ) -> EmployerInterview:

        sql = """
        INSERT INTO dbo.interviews (
            application_id,
            scheduled_start,
            scheduled_end,
            interview_type,
            location_or_link,
            interviewer_name,
            notes,
            status
        )
        OUTPUT INSERTED.id
        SELECT
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            N'scheduled'
        FROM dbo.applications AS a
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE a.id = ?
          AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                scheduled_start,
                scheduled_end,
                interview_type,
                location_or_link,
                interviewer_name,
                notes,
                application_id,
                organization_id,
            )
            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError(
                    "Application not found for this organization"
                )

            interview_id = str(row[0])
            connection.commit()

        interview = self.get_interview(
            organization_id,
            interview_id,
        )

        if interview is None:
            raise ValueError("Interview could not be loaded after creation")

        return interview

    def update_interview(
        self,
        organization_id: str,
        interview_id: str,
        scheduled_start,
        scheduled_end,
        interview_type: str,
        location_or_link: str,
        interviewer_name: str,
        notes: str,
        status: str,
    ) -> EmployerInterview | None:

        sql = """
        UPDATE i
        SET
            scheduled_start = ?,
            scheduled_end = ?,
            interview_type = ?,
            location_or_link = ?,
            interviewer_name = ?,
            notes = ?,
            status = ?,
            updated_at = SYSUTCDATETIME()
        FROM dbo.interviews AS i
        INNER JOIN dbo.applications AS a
            ON a.id = i.application_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE i.id = ?
          AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                scheduled_start,
                scheduled_end,
                interview_type,
                location_or_link,
                interviewer_name,
                notes,
                status,
                interview_id,
                organization_id,
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return None

            connection.commit()

        return self.get_interview(
            organization_id,
            interview_id,
        )
