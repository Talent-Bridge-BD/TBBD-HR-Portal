from abc import ABC, abstractmethod
from typing import Optional

import pyodbc

from models.visa_processing import VisaProcessing


ALLOWED_STATUSES = {
    "Pending",
    "Submitted",
    "Processing",
    "Approved",
    "Rejected",
    "Expired",
}


class VisaProcessingRepository(ABC):

    @abstractmethod
    def list_by_application(
        self,
        application_id: str,
        organization_id: Optional[str] = None,
    ) -> list[VisaProcessing]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        application_id: str,
        visa_type: Optional[str] = None,
        visa_number: Optional[str] = None,
        application_number: Optional[str] = None,
        submission_date=None,
        approval_date=None,
        expiry_date=None,
        status: str = "Pending",
        sponsor_name: Optional[str] = None,
        sponsor_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> VisaProcessing:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        visa_processing_id: str,
        organization_id: Optional[str] = None,
    ) -> Optional[VisaProcessing]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        visa_processing_id: str,
        visa_type: Optional[str] = None,
        visa_number: Optional[str] = None,
        application_number: Optional[str] = None,
        submission_date=None,
        approval_date=None,
        expiry_date=None,
        status: Optional[str] = None,
        sponsor_name: Optional[str] = None,
        sponsor_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[VisaProcessing]:
        raise NotImplementedError


class SqlVisaProcessingRepository(VisaProcessingRepository):

    def _connect(self):
        from database import get_connection
        return get_connection()

    @staticmethod
    def _map(row) -> VisaProcessing:
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

    def list_by_application(
        self,
        application_id: str,
        organization_id: Optional[str] = None,
    ) -> list[VisaProcessing]:

        sql = """
            SELECT
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
            FROM dbo.visa_processing AS vp
            INNER JOIN dbo.applications AS a
                ON a.id = vp.application_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE vp.application_id = ?
        """

        params = [application_id]

        if organization_id:
            sql += """
                AND j.organization_id = ?
            """
            params.append(organization_id)

        sql += """
            ORDER BY
                vp.submission_date DESC,
                vp.created_at DESC
        """

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [self._map(row) for row in rows]

    def create(
        self,
        application_id: str,
        visa_type: Optional[str] = None,
        visa_number: Optional[str] = None,
        application_number: Optional[str] = None,
        submission_date=None,
        approval_date=None,
        expiry_date=None,
        status: str = "Pending",
        sponsor_name: Optional[str] = None,
        sponsor_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> VisaProcessing:

        sql = """
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
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
            conn.commit()

        return self._map(row)

    def get(
        self,
        visa_processing_id: str,
        organization_id: Optional[str] = None,
    ) -> Optional[VisaProcessing]:

        sql = """
            SELECT
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
            FROM dbo.visa_processing AS vp
            INNER JOIN dbo.applications AS a
                ON a.id = vp.application_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE vp.id = ?
        """

        params = [visa_processing_id]

        if organization_id:
            sql += """
                AND j.organization_id = ?
            """
            params.append(organization_id)

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()

        return self._map(row) if row else None

    def update(
        self,
        visa_processing_id: str,
        visa_type: Optional[str] = None,
        visa_number: Optional[str] = None,
        application_number: Optional[str] = None,
        submission_date=None,
        approval_date=None,
        expiry_date=None,
        status: Optional[str] = None,
        sponsor_name: Optional[str] = None,
        sponsor_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[VisaProcessing]:

        sql = """
            UPDATE dbo.visa_processing
            SET
                visa_type = ?,
                visa_number = ?,
                application_number = ?,
                submission_date = ?,
                approval_date = ?,
                expiry_date = ?,
                status = COALESCE(?, status),
                sponsor_name = ?,
                sponsor_reference = ?,
                notes = ?,
                updated_at = SYSUTCDATETIME()
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
            WHERE id = ?
        """

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
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
                visa_processing_id,
            )
            row = cursor.fetchone()
            conn.commit()

        return self._map(row) if row else None
