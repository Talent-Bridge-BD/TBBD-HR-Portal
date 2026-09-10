from abc import ABC, abstractmethod
import struct

from azure.identity import DefaultAzureCredential

from models.offer import EmployerOffer


class OfferRepository(ABC):

    @abstractmethod
    def list_offers(
        self,
        organization_id: str,
    ) -> list[EmployerOffer]:
        raise NotImplementedError

    @abstractmethod
    def get_offer(
        self,
        organization_id: str,
        offer_id: str,
    ) -> EmployerOffer | None:
        raise NotImplementedError

    @abstractmethod
    def create_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_date,
        expiry_date,
        start_date,
        employment_type: str,
        salary_compensation: str,
        currency: str,
        location: str,
        notes: str,
    ) -> EmployerOffer:
        raise NotImplementedError

    @abstractmethod
    def update_offer(
        self,
        organization_id: str,
        offer_id: str,
        offer_date,
        expiry_date,
        start_date,
        employment_type: str,
        salary_compensation: str,
        currency: str,
        location: str,
        notes: str,
        status: str,
    ) -> EmployerOffer | None:
        raise NotImplementedError


class SqlOfferRepository(OfferRepository):

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
    def _map_row(row) -> EmployerOffer:
        return EmployerOffer(
            id=str(row.id),
            application_id=str(row.application_id),
            candidate_id=str(row.candidate_id),
            job_id=str(row.job_id),
            candidate_first_name=row.first_name,
            candidate_last_name=row.last_name,
            candidate_email=row.email,
            job_title=row.job_title,
            offer_date=row.offer_date,
            expiry_date=row.expiry_date,
            start_date=row.start_date,
            employment_type=row.employment_type,
            salary_compensation=row.salary_compensation,
            currency=row.currency,
            location=row.location,
            notes=row.notes,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_offers(
        self,
        organization_id: str,
    ) -> list[EmployerOffer]:
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
            o.offer_date,
            o.expiry_date,
            o.start_date,
            o.employment_type,
            o.salary_compensation,
            o.currency,
            o.location,
            o.notes,
            o.status,
            o.created_at,
            o.updated_at
        FROM dbo.offers AS o
        INNER JOIN dbo.applications AS a
            ON a.id = o.application_id
        INNER JOIN dbo.candidates AS c
            ON c.id = a.candidate_id
        INNER JOIN dbo.jobs AS j
            ON j.id = a.job_id
        WHERE j.organization_id = ?
        ORDER BY o.offer_date DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, organization_id)
            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_offer(
        self,
        organization_id: str,
        offer_id: str,
    ) -> EmployerOffer | None:
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
            o.offer_date,
            o.expiry_date,
            o.start_date,
            o.employment_type,
            o.salary_compensation,
            o.currency,
            o.location,
            o.notes,
            o.status,
            o.created_at,
            o.updated_at
        FROM dbo.offers AS o
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
                offer_id,
                organization_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def create_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_date,
        expiry_date,
        start_date,
        employment_type: str,
        salary_compensation: str,
        currency: str,
        location: str,
        notes: str,
    ) -> EmployerOffer:
        sql = """
        INSERT INTO dbo.offers (
            application_id,
            offer_date,
            expiry_date,
            start_date,
            employment_type,
            salary_compensation,
            currency,
            location,
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
            ?,
            ?,
            N'draft'
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
                offer_date,
                expiry_date,
                start_date,
                employment_type,
                salary_compensation,
                currency,
                location,
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

            offer_id = str(row[0])
            connection.commit()

        offer = self.get_offer(
            organization_id,
            offer_id,
        )

        if offer is None:
            raise ValueError(
                "Offer could not be loaded after creation"
            )

        return offer

    def update_offer(
        self,
        organization_id: str,
        offer_id: str,
        offer_date,
        expiry_date,
        start_date,
        employment_type: str,
        salary_compensation: str,
        currency: str,
        location: str,
        notes: str,
        status: str,
    ) -> EmployerOffer | None:
        sql = """
        UPDATE o
        SET
            offer_date = ?,
            expiry_date = ?,
            start_date = ?,
            employment_type = ?,
            salary_compensation = ?,
            currency = ?,
            location = ?,
            notes = ?,
            status = ?,
            updated_at = SYSUTCDATETIME()
        FROM dbo.offers AS o
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
                offer_date,
                expiry_date,
                start_date,
                employment_type,
                salary_compensation,
                currency,
                location,
                notes,
                status,
                offer_id,
                organization_id,
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return None

            connection.commit()

        return self.get_offer(
            organization_id,
            offer_id,
        )
