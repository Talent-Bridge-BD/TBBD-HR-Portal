from abc import ABC, abstractmethod
import struct

from azure.identity import DefaultAzureCredential

from models.onboarding import OnboardingRecord


class OnboardingRepository(ABC):

    @abstractmethod
    def list_onboarding(
        self,
        organization_id: str,
    ) -> list[OnboardingRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
    ) -> OnboardingRecord | None:
        raise NotImplementedError

    @abstractmethod
    def create_onboarding(
        self,
        organization_id: str,
        application_id: str,
        status: str,
        planned_start_date,
        employment_type: str | None,
        notes: str | None,
    ) -> OnboardingRecord:
        raise NotImplementedError

    @abstractmethod
    def update_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
        status: str,
        planned_start_date,
        employment_type: str | None,
        notes: str | None,
    ) -> OnboardingRecord | None:
        raise NotImplementedError

    @abstractmethod
    def delete_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
    ) -> bool:
        raise NotImplementedError


class SqlOnboardingRepository(OnboardingRepository):

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
    def _map_row(row) -> OnboardingRecord:
        return OnboardingRecord(
            id=str(row.id),
            application_id=str(row.application_id),
            candidate_id=str(row.candidate_id),
            job_id=str(row.job_id),
            candidate_first_name=row.first_name,
            candidate_last_name=row.last_name,
            candidate_email=row.email,
            job_title=row.job_title,
            status=row.status,
            planned_start_date=row.planned_start_date,
            employment_type=row.employment_type,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_onboarding(
        self,
        organization_id: str,
    ) -> list[OnboardingRecord]:
        sql = """
        SELECT
            o.id,
            o.application_id,
            a.candidate_id,
            a.job_id,
            c.first_name,
            c.last_name,
            c.email,
            j.title AS job_title,
            o.status,
            o.planned_start_date,
            o.employment_type,
            o.notes,
            o.created_at,
            o.updated_at
        FROM dbo.onboarding AS o
        INNER JOIN dbo.applications AS a
            ON a.id = o.application_id
        INNER JOIN dbo.candidates AS c
            ON c.id = a.candidate_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE j.organization_id = ?
        ORDER BY o.created_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, organization_id)
            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
    ) -> OnboardingRecord | None:
        sql = """
        SELECT
            o.id,
            o.application_id,
            a.candidate_id,
            a.job_id,
            c.first_name,
            c.last_name,
            c.email,
            j.title AS job_title,
            o.status,
            o.planned_start_date,
            o.employment_type,
            o.notes,
            o.created_at,
            o.updated_at
        FROM dbo.onboarding AS o
        INNER JOIN dbo.applications AS a
            ON a.id = o.application_id
        INNER JOIN dbo.candidates AS c
            ON c.id = a.candidate_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE o.id = ?
          AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                onboarding_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def create_onboarding(
        self,
        organization_id: str,
        application_id: str,
        status: str,
        planned_start_date,
        employment_type: str | None,
        notes: str | None,
    ) -> OnboardingRecord:
        sql = """
        INSERT INTO dbo.onboarding (
            application_id,
            status,
            planned_start_date,
            employment_type,
            notes
        )
        OUTPUT INSERTED.id
        SELECT
            ?,
            ?,
            ?,
            ?,
            ?
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
                status,
                planned_start_date,
                employment_type,
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

            onboarding_id = str(row[0])
            connection.commit()

        onboarding = self.get_onboarding(
            organization_id,
            onboarding_id,
        )

        if onboarding is None:
            raise ValueError(
                "Onboarding could not be loaded after creation"
            )

        return onboarding

    def update_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
        status: str,
        planned_start_date,
        employment_type: str | None,
        notes: str | None,
    ) -> OnboardingRecord | None:
        sql = """
        UPDATE o
        SET
            status = ?,
            planned_start_date = ?,
            employment_type = ?,
            notes = ?,
            updated_at = SYSUTCDATETIME()
        FROM dbo.onboarding AS o
        INNER JOIN dbo.applications AS a
            ON a.id = o.application_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE o.id = ?
          AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                status,
                planned_start_date,
                employment_type,
                notes,
                onboarding_id,
                organization_id,
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return None

            connection.commit()

        return self.get_onboarding(
            organization_id,
            onboarding_id,
        )

    def delete_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
    ) -> bool:
        sql = """
        DELETE o
        FROM dbo.onboarding AS o
        INNER JOIN dbo.applications AS a
            ON a.id = o.application_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE o.id = ?
          AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                onboarding_id,
                organization_id,
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return False

            connection.commit()

        return True
