from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.job_compensation import JobCompensation


class JobCompensationRepository(ABC):
    @abstractmethod
    def get_by_job_id(self, job_id: str) -> Optional[JobCompensation]:
        raise NotImplementedError

    @abstractmethod
    def save(self, compensation: JobCompensation) -> JobCompensation:
        raise NotImplementedError


class InMemoryJobCompensationRepository(JobCompensationRepository):
    def __init__(self):
        self._items: dict[str, JobCompensation] = {}

    def get_by_job_id(self, job_id: str) -> Optional[JobCompensation]:
        for item in self._items.values():
            if item.job_id == job_id:
                return item
        return None

    def save(self, compensation: JobCompensation) -> JobCompensation:
        self._items[compensation.id] = compensation
        return compensation


class SqlJobCompensationRepository(JobCompensationRepository):
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
    def _row_to_compensation(
        row: pyodbc.Row,
    ) -> JobCompensation:
        return JobCompensation(
            id=str(row.id),
            job_id=str(row.job_id),
            salary_currency=row.salary_currency,
            basic_salary=(
                Decimal(str(row.basic_salary))
                if row.basic_salary is not None
                else None
            ),
            overtime_rate=(
                Decimal(str(row.overtime_rate))
                if row.overtime_rate is not None
                else None
            ),
            food_provided=bool(row.food_provided),
            accommodation_provided=bool(row.accommodation_provided),
            transportation_provided=bool(row.transportation_provided),
            medical_coverage=bool(row.medical_coverage),
            air_ticket_provided=bool(row.air_ticket_provided),
            leave_entitlement=row.leave_entitlement,
            other_benefits=row.other_benefits,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def get_by_job_id(
        self,
        job_id: str,
    ) -> Optional[JobCompensation]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    job_id,
                    salary_currency,
                    basic_salary,
                    overtime_rate,
                    food_provided,
                    accommodation_provided,
                    transportation_provided,
                    medical_coverage,
                    air_ticket_provided,
                    leave_entitlement,
                    other_benefits,
                    created_at,
                    updated_at
                FROM dbo.job_compensation
                WHERE job_id = ?
                """,
                job_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_compensation(row)

    def save(
        self,
        compensation: JobCompensation,
    ) -> JobCompensation:
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id
                FROM dbo.job_compensation
                WHERE job_id = ?
                """,
                compensation.job_id,
            )
            existing = cursor.fetchone()

            if existing is None:
                cursor.execute(
                    """
                    INSERT INTO dbo.job_compensation (
                        job_id,
                        salary_currency,
                        basic_salary,
                        overtime_rate,
                        food_provided,
                        accommodation_provided,
                        transportation_provided,
                        medical_coverage,
                        air_ticket_provided,
                        leave_entitlement,
                        other_benefits
                    )
                    OUTPUT
                        INSERTED.id,
                        INSERTED.job_id,
                        INSERTED.salary_currency,
                        INSERTED.basic_salary,
                        INSERTED.overtime_rate,
                        INSERTED.food_provided,
                        INSERTED.accommodation_provided,
                        INSERTED.transportation_provided,
                        INSERTED.medical_coverage,
                        INSERTED.air_ticket_provided,
                        INSERTED.leave_entitlement,
                        INSERTED.other_benefits,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    compensation.job_id,
                    compensation.salary_currency,
                    compensation.basic_salary,
                    compensation.overtime_rate,
                    compensation.food_provided,
                    compensation.accommodation_provided,
                    compensation.transportation_provided,
                    compensation.medical_coverage,
                    compensation.air_ticket_provided,
                    compensation.leave_entitlement,
                    compensation.other_benefits,
                )
            else:
                cursor.execute(
                    """
                    UPDATE dbo.job_compensation
                    SET
                        salary_currency = ?,
                        basic_salary = ?,
                        overtime_rate = ?,
                        food_provided = ?,
                        accommodation_provided = ?,
                        transportation_provided = ?,
                        medical_coverage = ?,
                        air_ticket_provided = ?,
                        leave_entitlement = ?,
                        other_benefits = ?,
                        updated_at = SYSUTCDATETIME()
                    OUTPUT
                        INSERTED.id,
                        INSERTED.job_id,
                        INSERTED.salary_currency,
                        INSERTED.basic_salary,
                        INSERTED.overtime_rate,
                        INSERTED.food_provided,
                        INSERTED.accommodation_provided,
                        INSERTED.transportation_provided,
                        INSERTED.medical_coverage,
                        INSERTED.air_ticket_provided,
                        INSERTED.leave_entitlement,
                        INSERTED.other_benefits,
                        INSERTED.created_at,
                        INSERTED.updated_at
                    WHERE job_id = ?
                    """,
                    compensation.salary_currency,
                    compensation.basic_salary,
                    compensation.overtime_rate,
                    compensation.food_provided,
                    compensation.accommodation_provided,
                    compensation.transportation_provided,
                    compensation.medical_coverage,
                    compensation.air_ticket_provided,
                    compensation.leave_entitlement,
                    compensation.other_benefits,
                    compensation.job_id,
                )

            row = cursor.fetchone()
            connection.commit()

            if row is None:
                raise RuntimeError(
                    "Job compensation save did not return a database row"
                )

            return self._row_to_compensation(row)
