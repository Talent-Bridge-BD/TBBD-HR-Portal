from abc import ABC, abstractmethod
from typing import Optional

from azure.identity import DefaultAzureCredential

import pyodbc

from models.hiring import HiringApplication


class HiringRepository(ABC):

    @abstractmethod
    def list_hiring_applications(
        self,
        organization_id: str,
    ) -> list[HiringApplication]:
        raise NotImplementedError

    @abstractmethod
    def get_hiring_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> Optional[HiringApplication]:
        raise NotImplementedError

    @abstractmethod
    def list_ready_for_hiring(
        self,
        organization_id: str,
    ) -> list[HiringApplication]:
        raise NotImplementedError

    @abstractmethod
    def get_readiness(
        self,
        organization_id: str,
        application_id: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def create_hiring_record(
        self,
        organization_id: str,
        application_id: str,
        readiness_source: str,
        waiver_reason: Optional[str] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def get_hiring_record(
        self,
        organization_id: str,
        application_id: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def create_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_title: str,
        employment_type: Optional[str] = None,
        salary_amount=None,
        salary_currency: Optional[str] = None,
        start_date=None,
        offer_expiry_date=None,
        terms_and_conditions: Optional[str] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def update_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
        status: str,
        offer_title: str,
        employment_type: Optional[str] = None,
        salary_amount=None,
        salary_currency: Optional[str] = None,
        start_date=None,
        offer_expiry_date=None,
        terms_and_conditions: Optional[str] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def get_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
    ):
        raise NotImplementedError

    def hire(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
    ):
        raise NotImplementedError


class SqlHiringRepository(HiringRepository):

    def __init__(self):
        self.server = "tbbd-sql-sea.database.windows.net"
        self.database = "tbbd-hr-db"
        self.credential = DefaultAzureCredential()

    def _connection(self):
        token = self.credential.get_token(
            "https://database.windows.net/.default"
        ).token
        token_bytes = token.encode("utf-16-le")
        token_struct = (
            len(token_bytes).to_bytes(4, "little")
            + token_bytes
        )
        return pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;",
            attrs_before={1256: token_struct},
        )

    @staticmethod
    def _map_row(row) -> HiringApplication:
        return HiringApplication(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            job_id=str(row.job_id),
            candidate_first_name=row.first_name,
            candidate_last_name=row.last_name,
            candidate_email=row.email,
            candidate_phone=row.phone,
            job_title=row.job_title,
            status=row.status,
            workflow_status=row.workflow_status or "Applied",
            hiring_status=row.hiring_status,
            hiring_record_id=(
                str(row.hiring_record_id)
                if row.hiring_record_id
                else None
            ),
            applied_at=row.applied_at,
            updated_at=row.updated_at,
        )

    def list_hiring_applications(
        self,
        organization_id: str,
    ) -> list[HiringApplication]:
        sql = """
            SELECT
                a.id,
                a.candidate_id,
                a.job_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                j.title AS job_title,
                a.status,
                c.workflow_status,
                hr.status AS hiring_status,
                hr.id AS hiring_record_id,
                a.applied_at,
                a.updated_at
            FROM dbo.applications AS a
            INNER JOIN dbo.candidates AS c
                ON c.id = a.candidate_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            LEFT JOIN dbo.hiring_records AS hr
                ON hr.application_id = a.id
            WHERE j.organization_id = ?
              AND a.status IN (
                  N'submitted',
                  N'under_review',
                  N'shortlisted',
                  N'interview',
                  N'offered',
                  N'hired'
              )
            ORDER BY a.updated_at DESC;
        """
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, organization_id)
            rows = cursor.fetchall()

        return [
            self._map_row(row)
            for row in rows
        ]

    def list_ready_for_hiring(
        self,
        organization_id: str,
    ) -> list[HiringApplication]:
        sql = """
            SELECT
                a.id,
                a.candidate_id,
                a.job_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                j.title AS job_title,
                a.status,
                c.workflow_status,
                NULL AS hiring_status,
                NULL AS hiring_record_id,
                a.applied_at,
                a.updated_at
            FROM dbo.applications AS a
            INNER JOIN dbo.candidates AS c
                ON c.id = a.candidate_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE j.organization_id = ?
              AND a.status = N'shortlisted'
              AND NOT EXISTS (
                  SELECT 1
                  FROM dbo.hiring_records AS hr
                  WHERE hr.application_id = a.id
              )
              AND (
                  EXISTS (
                      SELECT 1
                      FROM dbo.interviews AS i
                      WHERE i.application_id = a.id
                        AND i.status = N'completed'
                        AND i.outcome = N'Pass'
                  )
                  OR EXISTS (
                      SELECT 1
                      FROM dbo.trade_tests AS tt
                      WHERE tt.application_id = a.id
                        AND tt.status = N'Completed'
                        AND tt.result = N'Pass'
                  )
              )
            ORDER BY a.updated_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, organization_id)
            rows = cursor.fetchall()

        return [
            self._map_row(row)
            for row in rows
        ]

    def get_hiring_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> Optional[HiringApplication]:
        sql = """
            SELECT
                a.id,
                a.candidate_id,
                a.job_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                j.title AS job_title,
                a.status,
                c.workflow_status,
                hr.status AS hiring_status,
                hr.id AS hiring_record_id,
                a.applied_at,
                a.updated_at
            FROM dbo.applications AS a
            INNER JOIN dbo.candidates AS c
                ON c.id = a.candidate_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            LEFT JOIN dbo.hiring_records AS hr
                ON hr.application_id = a.id
            WHERE a.id = ?
              AND j.organization_id = ?;
        """
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def get_readiness(
        self,
        organization_id: str,
        application_id: str,
    ):
        sql = """
            SELECT
                a.id AS application_id,
                a.status AS application_status,

                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM dbo.interviews AS i
                        WHERE i.application_id = a.id
                          AND i.status = N'completed'
                          AND i.outcome = N'Pass'
                    )
                    THEN N'interview_pass'

                    WHEN EXISTS (
                        SELECT 1
                        FROM dbo.trade_tests AS tt
                        WHERE tt.application_id = a.id
                          AND tt.status = N'Completed'
                          AND tt.result = N'Pass'
                    )
                    THEN N'trade_test_pass'

                    ELSE NULL
                END AS readiness_source,

                hr.id AS hiring_record_id,
                hr.status AS hiring_status,
                hr.readiness_source AS stored_readiness_source,
                hr.waiver_reason

            FROM dbo.applications AS a
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            LEFT JOIN dbo.hiring_records AS hr
                ON hr.application_id = a.id
            WHERE a.id = ?
              AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "application_id": str(row.application_id),
            "application_status": row.application_status,
            "readiness_source": row.readiness_source,
            "hiring_record_id": (
                str(row.hiring_record_id)
                if row.hiring_record_id
                else None
            ),
            "hiring_status": row.hiring_status,
            "stored_readiness_source": row.stored_readiness_source,
            "waiver_reason": row.waiver_reason,
        }

    def create_hiring_record(
        self,
        organization_id: str,
        application_id: str,
        readiness_source: str,
        waiver_reason: Optional[str] = None,
    ):
        sql = """
            INSERT INTO dbo.hiring_records (
                application_id,
                status,
                readiness_source,
                waiver_reason
            )
            OUTPUT
                INSERTED.id,
                INSERTED.application_id,
                INSERTED.status,
                INSERTED.readiness_source,
                INSERTED.waiver_reason,
                INSERTED.created_at,
                INSERTED.updated_at
            SELECT
                a.id,
                N'ready_for_hiring',
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

            try:
                cursor.execute(
                    sql,
                    readiness_source,
                    waiver_reason,
                    application_id,
                    organization_id,
                )
                row = cursor.fetchone()

                if row is None:
                    connection.rollback()
                    raise ValueError(
                        "Application not found for this organization"
                    )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

        return {
            "id": str(row[0]),
            "application_id": str(row[1]),
            "status": row[2],
            "readiness_source": row[3],
            "waiver_reason": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        }

    def get_hiring_record(
        self,
        organization_id: str,
        application_id: str,
    ):
        sql = """
            SELECT
                hr.id,
                hr.application_id,
                hr.status,
                hr.readiness_source,
                hr.waiver_reason,
                hr.created_at,
                hr.updated_at
            FROM dbo.hiring_records AS hr
            INNER JOIN dbo.applications AS a
                ON a.id = hr.application_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE hr.application_id = ?
              AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": str(row[0]),
            "application_id": str(row[1]),
            "status": row[2],
            "readiness_source": row[3],
            "waiver_reason": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        }

    def create_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_title: str,
        employment_type: Optional[str] = None,
        salary_amount=None,
        salary_currency: Optional[str] = None,
        start_date=None,
        offer_expiry_date=None,
        terms_and_conditions: Optional[str] = None,
    ):
        sql = """
            INSERT INTO dbo.job_offers (
                hiring_record_id,
                application_id,
                offer_title,
                employment_type,
                salary_amount,
                salary_currency,
                start_date,
                offer_expiry_date,
                terms_and_conditions,
                status
            )
            OUTPUT
                INSERTED.id,
                INSERTED.hiring_record_id,
                INSERTED.application_id,
                INSERTED.offer_title,
                INSERTED.employment_type,
                INSERTED.salary_amount,
                INSERTED.salary_currency,
                INSERTED.start_date,
                INSERTED.offer_expiry_date,
                INSERTED.terms_and_conditions,
                INSERTED.status,
                INSERTED.offered_at,
                INSERTED.accepted_at,
                INSERTED.rejected_at,
                INSERTED.withdrawn_at,
                INSERTED.created_at,
                INSERTED.updated_at
            SELECT
                hr.id,
                a.id,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                N'Draft'
            FROM dbo.hiring_records AS hr
            INNER JOIN dbo.applications AS a
                ON a.id = hr.application_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE hr.application_id = ?
              AND hr.status = N'ready_for_hiring'
              AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    sql,
                    offer_title,
                    employment_type,
                    salary_amount,
                    salary_currency,
                    start_date,
                    offer_expiry_date,
                    terms_and_conditions,
                    application_id,
                    organization_id,
                )
                row = cursor.fetchone()

                if row is None:
                    connection.rollback()
                    raise ValueError(
                        "Application is not ready for hiring"
                    )

                cursor.execute(
                    '''
                    UPDATE dbo.hiring_records
                    SET
                        status = N'offered',
                        updated_at = SYSUTCDATETIME()
                    WHERE application_id = ?
                      AND status = N'ready_for_hiring'
                    ''',
                    application_id,
                )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

        return self._map_offer_row(row)

    def update_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
        status: str,
        offer_title: str,
        employment_type: Optional[str] = None,
        salary_amount=None,
        salary_currency: Optional[str] = None,
        start_date=None,
        offer_expiry_date=None,
        terms_and_conditions: Optional[str] = None,
    ):
        sql = """
            UPDATE o
            SET
                o.offer_title = ?,
                o.employment_type = ?,
                o.salary_amount = ?,
                o.salary_currency = ?,
                o.start_date = ?,
                o.offer_expiry_date = ?,
                o.terms_and_conditions = ?,
                o.status = ?,
                o.offered_at =
                    CASE
                        WHEN ? = N'Sent'
                             AND o.offered_at IS NULL
                        THEN SYSUTCDATETIME()
                        ELSE o.offered_at
                    END,
                o.accepted_at =
                    CASE
                        WHEN ? = N'Accepted'
                        THEN COALESCE(
                            o.accepted_at,
                            SYSUTCDATETIME()
                        )
                        ELSE o.accepted_at
                    END,
                o.rejected_at =
                    CASE
                        WHEN ? = N'Rejected'
                        THEN COALESCE(
                            o.rejected_at,
                            SYSUTCDATETIME()
                        )
                        ELSE o.rejected_at
                    END,
                o.withdrawn_at =
                    CASE
                        WHEN ? = N'Withdrawn'
                        THEN COALESCE(
                            o.withdrawn_at,
                            SYSUTCDATETIME()
                        )
                        ELSE o.withdrawn_at
                    END,
                o.updated_at = SYSUTCDATETIME()
            FROM dbo.job_offers AS o
            INNER JOIN dbo.hiring_records AS hr
                ON hr.id = o.hiring_record_id
            INNER JOIN dbo.applications AS a
                ON a.id = o.application_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE o.id = ?
              AND o.application_id = ?
              AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                offer_title,
                employment_type,
                salary_amount,
                salary_currency,
                start_date,
                offer_expiry_date,
                terms_and_conditions,
                status,
                status,
                status,
                status,
                status,
                offer_id,
                application_id,
                organization_id,
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return None

            cursor.execute(
                """
                SELECT
                    o.id,
                    o.hiring_record_id,
                    o.application_id,
                    o.offer_title,
                    o.employment_type,
                    o.salary_amount,
                    o.salary_currency,
                    o.start_date,
                    o.offer_expiry_date,
                    o.terms_and_conditions,
                    o.status,
                    o.offered_at,
                    o.accepted_at,
                    o.rejected_at,
                    o.withdrawn_at,
                    o.created_at,
                    o.updated_at
                FROM dbo.job_offers AS o
                INNER JOIN dbo.applications AS a
                    ON a.id = o.application_id
                INNER JOIN dbo.jobs AS j
                    ON j.id = a.job_id
                WHERE o.id = ?
                  AND o.application_id = ?
                  AND j.organization_id = ?;
                """,
                offer_id,
                application_id,
                organization_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                return None

            connection.commit()

        return self._map_offer_row(row)

    def get_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
    ):
        sql = """
            SELECT
                o.id,
                o.hiring_record_id,
                o.application_id,
                o.offer_title,
                o.employment_type,
                o.salary_amount,
                o.salary_currency,
                o.start_date,
                o.offer_expiry_date,
                o.terms_and_conditions,
                o.status,
                o.offered_at,
                o.accepted_at,
                o.rejected_at,
                o.withdrawn_at,
                o.created_at,
                o.updated_at
            FROM dbo.job_offers AS o
            INNER JOIN dbo.hiring_records AS hr
                ON hr.id = o.hiring_record_id
            INNER JOIN dbo.applications AS a
                ON a.id = o.application_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            WHERE o.id = ?
              AND o.application_id = ?
              AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                offer_id,
                application_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_offer_row(row)

    def hire(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
    ):
        sql = """
            UPDATE hr
            SET
                hr.status = N'hired',
                hr.updated_at = SYSUTCDATETIME()
            FROM dbo.hiring_records AS hr
            INNER JOIN dbo.applications AS a
                ON a.id = hr.application_id
            INNER JOIN dbo.jobs AS j
                ON j.id = a.job_id
            INNER JOIN dbo.job_offers AS o
                ON o.hiring_record_id = hr.id
               AND o.application_id = a.id
            WHERE hr.application_id = ?
              AND o.id = ?
              AND o.status = N'Accepted'
              AND hr.status = N'offered'
              AND j.organization_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                application_id,
                offer_id,
                organization_id,
            )

            if cursor.rowcount != 1:
                connection.rollback()
                raise ValueError(
                    "Accepted offer not found for this organization"
                )

            cursor.execute(
                """
                UPDATE a
                SET
                    a.status = N'hired',
                    a.updated_at = SYSUTCDATETIME()
                FROM dbo.applications AS a
                INNER JOIN dbo.jobs AS j
                    ON j.id = a.job_id
                WHERE a.id = ?
                  AND j.organization_id = ?;
                """,
                application_id,
                organization_id,
            )

            if cursor.rowcount != 1:
                connection.rollback()
                raise ValueError(
                    "Application could not be marked as hired."
                )

            connection.commit()

        return self.get_hiring_record(
            organization_id,
            application_id,
        )

    @staticmethod
    def _map_offer_row(row):
        return {
            "id": str(row[0]),
            "hiring_record_id": str(row[1]),
            "application_id": str(row[2]),
            "offer_title": row[3],
            "employment_type": row[4],
            "salary_amount": row[5],
            "salary_currency": row[6],
            "start_date": row[7],
            "offer_expiry_date": row[8],
            "terms_and_conditions": row[9],
            "status": row[10],
            "offered_at": row[11],
            "accepted_at": row[12],
            "rejected_at": row[13],
            "withdrawn_at": row[14],
            "created_at": row[15],
            "updated_at": row[16],
        }
