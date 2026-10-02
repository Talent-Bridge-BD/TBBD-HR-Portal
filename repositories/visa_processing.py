import struct
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from azure.identity import DefaultAzureCredential

from models.visa_processing import VisaProcessing


class VisaProcessingRepository(ABC):

    @abstractmethod
    def list_by_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> list[VisaProcessing]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        organization_id: str,
        application_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date: date | None = None,
        approval_date: date | None = None,
        expiry_date: date | None = None,
        status: str = "Pending",
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ) -> VisaProcessing:
        sql = """
        IF NOT EXISTS (
            SELECT 1
            FROM dbo.applications AS a
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE a.id = ?
              AND j.organization_id = ?
        )
        BEGIN
            THROW 50001, 'Application not found for organization', 1;
        END;

        INSERT INTO dbo.visa_processing (
            application_id,
            visa_type,
            visa_number,
            application_number,
            submission_date,
            approval_date,
            expiry_date,
            status,
            sponsor_name,
            sponsor_reference,
            notes
        )
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.visa_type,
            INSERTED.visa_number,
            INSERTED.application_number,
            INSERTED.submission_date,
            INSERTED.approval_date,
            INSERTED.expiry_date,
            INSERTED.status,
            INSERTED.sponsor_name,
            INSERTED.sponsor_reference,
            INSERTED.notes,
            INSERTED.created_at,
            INSERTED.updated_at
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        );
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                application_id,
                organization_id,
                application_id,
                visa_type,
                visa_number,
                application_number,
                submission_date,
                approval_date,
                expiry_date,
                status,
                sponsor_name,
                sponsor_reference,
                notes,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError(
                    "Visa processing record could not be created"
                )

            connection.commit()

        return self._map_row(row)

    def get(
        self,
        organization_id: str,
        visa_processing_id: str,
    ) -> VisaProcessing | None:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        organization_id: str,
        visa_processing_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date: date | None = None,
        approval_date: date | None = None,
        expiry_date: date | None = None,
        status: str | None = None,
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ) -> VisaProcessing:
        raise NotImplementedError


class SqlVisaProcessingRepository(VisaProcessingRepository):

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
    def _map_row(row) -> VisaProcessing:
        return VisaProcessing(
            id=str(row.id),
            application_id=str(row.application_id),
            visa_type=row.visa_type,
            visa_number=row.visa_number,
            application_number=row.application_number,
            submission_date=row.submission_date,
            approval_date=row.approval_date,
            expiry_date=row.expiry_date,
            status=row.status,
            sponsor_name=row.sponsor_name,
            sponsor_reference=row.sponsor_reference,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _select_columns() -> str:
        return """
            vp.id,
            vp.application_id,
            vp.visa_type,
            vp.visa_number,
            vp.application_number,
            vp.submission_date,
            vp.approval_date,
            vp.expiry_date,
            vp.status,
            vp.sponsor_name,
            vp.sponsor_reference,
            vp.notes,
            vp.created_at,
            vp.updated_at
        """

    def list_by_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> list[VisaProcessing]:
        sql = f"""
        SELECT
            {self._select_columns()}
        FROM dbo.visa_processing AS vp
        INNER JOIN dbo.applications AS a
            ON a.id = vp.application_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE j.organization_id = ?
          AND vp.application_id = ?
        ORDER BY
            vp.created_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                organization_id,
                application_id,
            )
            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def create(
        self,
        organization_id: str,
        application_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date: date | None = None,
        approval_date: date | None = None,
        expiry_date: date | None = None,
        status: str = "Pending",
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ) -> VisaProcessing:
        sql = """
        IF NOT EXISTS (
            SELECT 1
            FROM dbo.applications AS a
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE a.id = ?
              AND j.organization_id = ?
        )
        BEGIN
            THROW 50001, 'Application not found for organization', 1;
        END;

        INSERT INTO dbo.visa_processing (
            application_id,
            visa_type,
            visa_number,
            application_number,
            submission_date,
            approval_date,
            expiry_date,
            status,
            sponsor_name,
            sponsor_reference,
            notes
        )
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.visa_type,
            INSERTED.visa_number,
            INSERTED.application_number,
            INSERTED.submission_date,
            INSERTED.approval_date,
            INSERTED.expiry_date,
            INSERTED.status,
            INSERTED.sponsor_name,
            INSERTED.sponsor_reference,
            INSERTED.notes,
            INSERTED.created_at,
            INSERTED.updated_at
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        );
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                application_id,
                organization_id,
                application_id,
                visa_type,
                visa_number,
                application_number,
                submission_date,
                approval_date,
                expiry_date,
                status,
                sponsor_name,
                sponsor_reference,
                notes,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError(
                    "Visa processing record could not be created"
                )

            connection.commit()

        return self._map_row(row)

    def get(
        self,
        organization_id: str,
        visa_processing_id: str,
    ) -> VisaProcessing | None:
        sql = f"""
        SELECT
            {self._select_columns()}
        FROM dbo.visa_processing AS vp
        INNER JOIN dbo.applications AS a
            ON a.id = vp.application_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE vp.id = ?
          AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                visa_processing_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def update(
        self,
        organization_id: str,
        visa_processing_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date: date | None = None,
        approval_date: date | None = None,
        expiry_date: date | None = None,
        status: str | None = None,
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ) -> VisaProcessing:
        fields = []
        values = []

        if visa_type is not None:
            fields.append("visa_type = ?")
            values.append(visa_type)

        if visa_number is not None:
            fields.append("visa_number = ?")
            values.append(visa_number)

        if application_number is not None:
            fields.append("application_number = ?")
            values.append(application_number)

        if submission_date is not None:
            fields.append("submission_date = ?")
            values.append(submission_date)

        if approval_date is not None:
            fields.append("approval_date = ?")
            values.append(approval_date)

        if expiry_date is not None:
            fields.append("expiry_date = ?")
            values.append(expiry_date)

        if status is not None:
            fields.append("status = ?")
            values.append(status)

        if sponsor_name is not None:
            fields.append("sponsor_name = ?")
            values.append(sponsor_name)

        if sponsor_reference is not None:
            fields.append("sponsor_reference = ?")
            values.append(sponsor_reference)

        if notes is not None:
            fields.append("notes = ?")
            values.append(notes)

        fields.append("updated_at = SYSUTCDATETIME()")

        sql = f"""
        UPDATE vp
        SET
            {", ".join(fields)}
        OUTPUT
            {self._select_columns()}
        FROM dbo.visa_processing AS vp
        INNER JOIN dbo.applications AS a
            ON a.id = vp.application_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE vp.id = ?
          AND j.organization_id = ?;
        """

        values.extend([
            visa_processing_id,
            organization_id,
        ])

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, *values)

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError("Visa processing record not found")

            connection.commit()

        return self._map_row(row)
