from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.job import Job


class JobRepository(ABC):
    @abstractmethod
    def list_jobs(self, organization_id: str) -> list[Job]:
        raise NotImplementedError

    @abstractmethod
    def list_all_active_organization_jobs(self) -> list[Job]:
        raise NotImplementedError

    @abstractmethod
    def list_published_jobs(self) -> list[Job]:
        raise NotImplementedError

    @abstractmethod
    def get_published_job(
        self,
        job_id: str,
    ) -> Optional[Job]:
        raise NotImplementedError

    def get_job(
        self,
        organization_id: str,
        job_id: str,
    ) -> Optional[Job]:
        raise NotImplementedError

    @abstractmethod
    def save_job(self, job: Job) -> Job:
        raise NotImplementedError


class InMemoryJobRepository(JobRepository):
    def __init__(self):
        self._jobs: dict[str, Job] = {}

    def list_jobs(self, organization_id: str) -> list[Job]:
        return [
            job
            for job in self._jobs.values()
            if job.organization_id == organization_id
        ]

    def list_all_active_organization_jobs(self) -> list[Job]:
        return list(self._jobs.values())

    def list_published_jobs(self) -> list[Job]:
        return [
            job
            for job in self._jobs.values()
            if job.status == "open"
            and job.published_at is not None
        ]

    def get_published_job(
        self,
        job_id: str,
    ) -> Optional[Job]:
        job = self._jobs.get(job_id)
        if job is None:
            return None
        if job.status != "open" or job.published_at is None:
            return None
        return job

    def get_job(
        self,
        organization_id: str,
        job_id: str,
    ) -> Optional[Job]:
        job = self._jobs.get(job_id)
        if job is None or job.organization_id != organization_id:
            return None
        return job

    def save_job(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job


class SqlJobRepository(JobRepository):
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

    @staticmethod
    def _row_to_job(row: pyodbc.Row) -> Job:
        return Job(
            id=str(row.id),
            organization_id=str(row.organization_id),
            title=row.title,
            description=row.description,
            employment_type=row.employment_type,
            location=row.location,
            country=row.country,
            status=row.status,
            number_of_positions=row.number_of_positions,
            requisition_number=row.job_reference,
            employer_name=row.employer_name,
            employer_country=row.employer_country,
            employer_city=row.employer_city,
            trade_skill_category=row.job_category,
            industry_sector=row.industry_sector,
            gender_requirement=row.gender_requirement,
            minimum_age=row.minimum_age,
            maximum_age=row.maximum_age,
            contract_duration=row.contract_duration,
            work_location=row.work_location,
            project_name=row.project_name,
            published_at=row.published_at,
            closing_at=row.closing_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_all_active_organization_jobs(self) -> list[Job]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    j.id,
                    j.organization_id,
                    j.title,
                    j.description,
                    j.employment_type,
                    j.location,
                    j.country,
                    j.status,
                    j.number_of_positions,
                    j.job_reference,
                    j.employer_name,
                    j.employer_country,
                    j.employer_city,
                    j.job_category,
                    j.industry_sector,
                    j.gender_requirement,
                    j.minimum_age,
                    j.maximum_age,
                    j.contract_duration,
                    j.work_location,
                    j.project_name,
                    j.published_at,
                    j.closing_at,
                    j.created_at,
                    j.updated_at
                FROM dbo.jobs AS j
                INNER JOIN dbo.organizations AS o
                    ON o.id = j.organization_id
                WHERE o.status = N'active'
                ORDER BY j.created_at DESC
                """,
            )
            return [
                self._row_to_job(row)
                for row in cursor.fetchall()
            ]

    def list_jobs(self, organization_id: str) -> list[Job]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    organization_id,
                    title,
                    description,
                    employment_type,
                    location,
                    country,
                    status,
                    number_of_positions,
                    job_reference,
                    employer_name,
                    employer_country,
                    employer_city,
                    job_category,
                    industry_sector,
                    gender_requirement,
                    minimum_age,
                    maximum_age,
                    contract_duration,
                    work_location,
                    project_name,
                    published_at,
                    closing_at,
                    created_at,
                    updated_at
                FROM dbo.jobs
                WHERE organization_id = ?
                ORDER BY created_at DESC
                """,
                organization_id,
            )
            return [
                self._row_to_job(row)
                for row in cursor.fetchall()
            ]

    def list_published_jobs(self) -> list[Job]:
        sql = """
            SELECT
                id,
                organization_id,
                title,
                description,
                employment_type,
                location,
                country,
                status,
                number_of_positions,
                job_reference,
                employer_name,
                employer_country,
                employer_city,
                job_category,
                industry_sector,
                gender_requirement,
                minimum_age,
                maximum_age,
                contract_duration,
                work_location,
                project_name,
                published_at,
                closing_at,
                created_at,
                updated_at
            FROM dbo.jobs
            WHERE status = 'open'
              AND published_at IS NOT NULL
              AND published_at <= SYSUTCDATETIME()
              AND (
                    closing_at IS NULL
                    OR closing_at > SYSUTCDATETIME()
              )
            ORDER BY published_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()

        return [
            self._row_to_job(row)
            for row in rows
        ]

    def get_published_job(
        self,
        job_id: str,
    ) -> Optional[Job]:
        sql = """
            SELECT
                id,
                organization_id,
                title,
                description,
                employment_type,
                location,
                country,
                status,
                number_of_positions,
                job_reference,
                employer_name,
                employer_country,
                employer_city,
                job_category,
                industry_sector,
                gender_requirement,
                minimum_age,
                maximum_age,
                contract_duration,
                work_location,
                project_name,
                published_at,
                closing_at,
                created_at,
                updated_at
            FROM dbo.jobs
            WHERE id = ?
              AND status = 'open'
              AND published_at IS NOT NULL
              AND published_at <= SYSUTCDATETIME()
              AND (
                    closing_at IS NULL
                    OR closing_at > SYSUTCDATETIME()
              )
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, job_id)
            row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_job(row)

    def get_job(
        self,
        organization_id: str,
        job_id: str,
    ) -> Optional[Job]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    organization_id,
                    title,
                    description,
                    employment_type,
                    location,
                    country,
                    status,
                    number_of_positions,
                    job_reference,
                    employer_name,
                    employer_country,
                    employer_city,
                    job_category,
                    industry_sector,
                    gender_requirement,
                    minimum_age,
                    maximum_age,
                    contract_duration,
                    work_location,
                    project_name,
                    published_at,
                    closing_at,
                    created_at,
                    updated_at
                FROM dbo.jobs
                WHERE organization_id = ?
                  AND id = ?
                """,
                organization_id,
                job_id,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_job(row)

    def save_job(self, job: Job) -> Job:
        with self._connection() as connection:
            cursor = connection.cursor()

            if job.id:
                cursor.execute(
                    """
                    SELECT id
                    FROM dbo.jobs
                    WHERE id = ?
                      AND organization_id = ?
                    """,
                    job.id,
                    job.organization_id,
                )
                existing = cursor.fetchone()
            else:
                existing = None

            if existing is None:
                cursor.execute(
                    """
                    INSERT INTO dbo.jobs (
                        organization_id,
                        title,
                        description,
                        employment_type,
                        location,
                        country,
                        status,
                        number_of_positions,
                        job_reference,
                        employer_name,
                        employer_country,
                        employer_city,
                        job_category,
                        industry_sector,
                        gender_requirement,
                        minimum_age,
                        maximum_age,
                        contract_duration,
                        work_location,
                        project_name,
                        published_at,
                        closing_at
                    )
                    OUTPUT
                        INSERTED.id,
                        INSERTED.organization_id,
                        INSERTED.title,
                        INSERTED.description,
                        INSERTED.employment_type,
                        INSERTED.location,
                        INSERTED.country,
                        INSERTED.status,
                        INSERTED.number_of_positions,
                        INSERTED.job_reference,
                        INSERTED.employer_name,
                        INSERTED.employer_country,
                        INSERTED.employer_city,
                        INSERTED.job_category,
                        INSERTED.industry_sector,
                        INSERTED.gender_requirement,
                        INSERTED.minimum_age,
                        INSERTED.maximum_age,
                        INSERTED.contract_duration,
                        INSERTED.work_location,
                        INSERTED.project_name,
                        INSERTED.published_at,
                        INSERTED.closing_at,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    job.organization_id,
                    job.title,
                    job.description,
                    job.employment_type,
                    job.location,
                    job.country,
                    job.status,
                    job.number_of_positions,
                    job.requisition_number,
                    job.employer_name,
                    job.employer_country,
                    job.employer_city,
                    job.trade_skill_category,
                    job.industry_sector,
                    job.gender_requirement,
                    job.minimum_age,
                    job.maximum_age,
                    job.contract_duration,
                    job.work_location,
                    job.project_name,
                    job.published_at,
                    job.closing_at,
                )
            else:
                cursor.execute(
                    """
                    UPDATE dbo.jobs
                    SET
                        title = ?,
                        description = ?,
                        employment_type = ?,
                        location = ?,
                        country = ?,
                        status = ?,
                        number_of_positions = ?,
                        job_reference = ?,
                        employer_name = ?,
                        employer_country = ?,
                        employer_city = ?,
                        job_category = ?,
                        industry_sector = ?,
                        gender_requirement = ?,
                        minimum_age = ?,
                        maximum_age = ?,
                        contract_duration = ?,
                        work_location = ?,
                        project_name = ?,
                        published_at = ?,
                        closing_at = ?,
                        updated_at = SYSUTCDATETIME()
                    OUTPUT
                        INSERTED.id,
                        INSERTED.organization_id,
                        INSERTED.title,
                        INSERTED.description,
                        INSERTED.employment_type,
                        INSERTED.location,
                        INSERTED.country,
                        INSERTED.status,
                        INSERTED.number_of_positions,
                        INSERTED.job_reference,
                        INSERTED.employer_name,
                        INSERTED.employer_country,
                        INSERTED.employer_city,
                        INSERTED.job_category,
                        INSERTED.industry_sector,
                        INSERTED.gender_requirement,
                        INSERTED.minimum_age,
                        INSERTED.maximum_age,
                        INSERTED.contract_duration,
                        INSERTED.work_location,
                        INSERTED.project_name,
                        INSERTED.published_at,
                        INSERTED.closing_at,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    WHERE id = ?
                      AND organization_id = ?
                    """,
                    job.title,
                    job.description,
                    job.employment_type,
                    job.location,
                    job.country,
                    job.status,
                    job.number_of_positions,
                    job.requisition_number,
                    job.employer_name,
                    job.employer_country,
                    job.employer_city,
                    job.trade_skill_category,
                    job.industry_sector,
                    job.gender_requirement,
                    job.minimum_age,
                    job.maximum_age,
                    job.contract_duration,
                    job.work_location,
                    job.project_name,
                    job.published_at,
                    job.closing_at,
                    job.id,
                    job.organization_id,
                )

            row = cursor.fetchone()
            connection.commit()

            if row is None:
                raise RuntimeError("Job save did not return a database row")

            return self._row_to_job(row)
