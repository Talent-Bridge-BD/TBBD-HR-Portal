from __future__ import annotations

import os
import struct
from datetime import datetime, timezone
from abc import ABC, abstractmethod

import pyodbc
from azure.identity import DefaultAzureCredential

from models.employer_dashboard import (
    EmployerDashboard,
    EmployerDashboardStats,
    EmployerPipeline,
)
from services.authorization import AuthorizationContext


class EmployerDashboardRepository(ABC):
    @abstractmethod
    def get_dashboard(
        self,
        context: AuthorizationContext,
        employer_name: str,
    ) -> EmployerDashboard:
        raise NotImplementedError


class InMemoryEmployerDashboardRepository(EmployerDashboardRepository):
    def __init__(self, dashboard: EmployerDashboard | None = None):
        self.dashboard = dashboard

    def get_dashboard(
        self,
        context: AuthorizationContext,
        employer_name: str,
    ) -> EmployerDashboard:
        if self.dashboard is None:
            raise RuntimeError("Employer dashboard test data has not been configured")

        return EmployerDashboard(
            employer_name=employer_name,
            organization_name=self.dashboard.organization_name,
            stats=self.dashboard.stats,
            pipeline=self.dashboard.pipeline,
        )


class SqlEmployerDashboardRepository(EmployerDashboardRepository):
    """
    Azure SQL implementation for the Employer Dashboard.

    All recruitment queries are restricted to organizations contained
    in AuthorizationContext.organization_ids.
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
    def _organization_placeholders(organization_ids: list[str]) -> str:
        return ", ".join("?" for _ in organization_ids)

    def get_dashboard(
        self,
        context: AuthorizationContext,
        employer_name: str,
    ) -> EmployerDashboard:
        organization_ids = sorted(context.organization_ids)

        if not organization_ids:
            return EmployerDashboard(
                employer_name=employer_name,
                organization_name=None,
                stats=EmployerDashboardStats(
                    active_jobs=0,
                    new_applications=0,
                    candidates_pipeline=0,
                    interviews_upcoming=0,
                ),
                pipeline=EmployerPipeline(
                    new=0,
                    screening=0,
                    shortlisted=0,
                    interview=0,
                    offer=0,
                    hired=0,
                ),
            )

        placeholders = self._organization_placeholders(organization_ids)

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM dbo.jobs
                WHERE organization_id IN ({placeholders})
                  AND status = N'open'
                """,
                *organization_ids,
            )
            active_jobs = int(cursor.fetchone()[0])

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM dbo.applications AS a
                INNER JOIN dbo.jobs AS j
                    ON j.id = a.job_id
                WHERE j.organization_id IN ({placeholders})
                  AND a.status = N'submitted'
                """,
                *organization_ids,
            )
            new_applications = int(cursor.fetchone()[0])

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM dbo.applications AS a
                INNER JOIN dbo.jobs AS j
                    ON j.id = a.job_id
                WHERE j.organization_id IN ({placeholders})
                  AND a.status NOT IN (N'rejected', N'withdrawn')
                """,
                *organization_ids,
            )
            candidates_pipeline = int(cursor.fetchone()[0])

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM dbo.interviews AS i
                INNER JOIN dbo.applications AS a
                    ON a.id = i.application_id
                INNER JOIN dbo.jobs AS j
                    ON j.id = a.job_id
                WHERE j.organization_id IN ({placeholders})
                  AND i.status IN (N'scheduled', N'rescheduled')
                  AND i.scheduled_start >= SYSUTCDATETIME()
                """,
                *organization_ids,
            )
            interviews_upcoming = int(cursor.fetchone()[0])

            cursor.execute(
                f"""
                SELECT
                    a.status,
                    COUNT(*) AS status_count
                FROM dbo.applications AS a
                INNER JOIN dbo.jobs AS j
                    ON j.id = a.job_id
                WHERE j.organization_id IN ({placeholders})
                GROUP BY a.status
                """,
                *organization_ids,
            )

            pipeline_counts = {
                "submitted": 0,
                "under_review": 0,
                "shortlisted": 0,
                "interview": 0,
                "offered": 0,
                "hired": 0,
            }

            for row in cursor.fetchall():
                if row.status in pipeline_counts:
                    pipeline_counts[row.status] = int(row.status_count)

            cursor.execute(
                f"""
                SELECT TOP (1)
                    o.name
                FROM dbo.organizations AS o
                WHERE CONVERT(nvarchar(36), o.id) IN ({placeholders})
                  AND o.status = N'active'
                ORDER BY o.name
                """,
                *organization_ids,
            )
            organization_row = cursor.fetchone()

            organization_name = (
                str(organization_row.name)
                if organization_row is not None
                else None
            )

            return EmployerDashboard(
                employer_name=employer_name,
                organization_name=organization_name,
                stats=EmployerDashboardStats(
                    active_jobs=active_jobs,
                    new_applications=new_applications,
                    candidates_pipeline=candidates_pipeline,
                    interviews_upcoming=interviews_upcoming,
                ),
                pipeline=EmployerPipeline(
                    new=pipeline_counts["submitted"],
                    screening=pipeline_counts["under_review"],
                    shortlisted=pipeline_counts["shortlisted"],
                    interview=pipeline_counts["interview"],
                    offer=pipeline_counts["offered"],
                    hired=pipeline_counts["hired"],
                ),
            )
