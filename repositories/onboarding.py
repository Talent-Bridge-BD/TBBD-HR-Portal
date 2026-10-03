import struct

from abc import ABC, abstractmethod

from azure.identity import DefaultAzureCredential

from models.onboarding import Onboarding


class OnboardingRepository(ABC):

    @abstractmethod
    def list_by_application(
        self,
        application_id: str,
    ) -> list[Onboarding]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        application_id: str,
        employer_name: str | None = None,
        job_title: str | None = None,
        joining_date=None,
        status: str = "Pending",
        contract_signed: bool = False,
        documents_verified: bool = False,
        orientation_completed: bool = False,
        accommodation_arranged: bool = False,
        transport_arranged: bool = False,
        notes: str | None = None,
    ) -> Onboarding:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        onboarding_id: str,
    ) -> Onboarding | None:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        onboarding_id: str,
        employer_name: str | None = None,
        job_title: str | None = None,
        joining_date=None,
        status: str | None = None,
        contract_signed: bool | None = None,
        documents_verified: bool | None = None,
        orientation_completed: bool | None = None,
        accommodation_arranged: bool | None = None,
        transport_arranged: bool | None = None,
        notes: str | None = None,
        completed_at=None,
    ) -> Onboarding:
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

        token = self.credential.get_token(
            self.SQL_SCOPE
        ).token

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
    def _map_row(row) -> Onboarding:
        return Onboarding(
            id=str(row.id),
            application_id=str(row.application_id),
            employer_name=row.employer_name,
            job_title=row.job_title,
            joining_date=row.joining_date,
            status=row.status,
            contract_signed=bool(row.contract_signed),
            documents_verified=bool(row.documents_verified),
            orientation_completed=bool(row.orientation_completed),
            accommodation_arranged=bool(row.accommodation_arranged),
            transport_arranged=bool(row.transport_arranged),
            notes=row.notes,
            completed_at=row.completed_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_by_application(
        self,
        application_id: str,
    ) -> list[Onboarding]:
        sql = """
        SELECT
            id,
            application_id,
            employer_name,
            job_title,
            joining_date,
            status,
            contract_signed,
            documents_verified,
            orientation_completed,
            accommodation_arranged,
            transport_arranged,
            notes,
            completed_at,
            created_at,
            updated_at
        FROM dbo.onboarding
        WHERE application_id = ?
        ORDER BY created_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
            )
            rows = cursor.fetchall()

        return [
            self._map_row(row)
            for row in rows
        ]

    def create(
        self,
        application_id: str,
        employer_name: str | None = None,
        job_title: str | None = None,
        joining_date=None,
        status: str = "Pending",
        contract_signed: bool = False,
        documents_verified: bool = False,
        orientation_completed: bool = False,
        accommodation_arranged: bool = False,
        transport_arranged: bool = False,
        notes: str | None = None,
    ) -> Onboarding:
        sql = """
        INSERT INTO dbo.onboarding (
            application_id,
            employer_name,
            job_title,
            joining_date,
            status,
            contract_signed,
            documents_verified,
            orientation_completed,
            accommodation_arranged,
            transport_arranged,
            notes
        )
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.employer_name,
            INSERTED.job_title,
            INSERTED.joining_date,
            INSERTED.status,
            INSERTED.contract_signed,
            INSERTED.documents_verified,
            INSERTED.orientation_completed,
            INSERTED.accommodation_arranged,
            INSERTED.transport_arranged,
            INSERTED.notes,
            INSERTED.completed_at,
            INSERTED.created_at,
            INSERTED.updated_at
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                employer_name,
                job_title,
                joining_date,
                status,
                contract_signed,
                documents_verified,
                orientation_completed,
                accommodation_arranged,
                transport_arranged,
                notes,
            )
            row = cursor.fetchone()
            connection.commit()

        return self._map_row(row)

    def get(
        self,
        onboarding_id: str,
    ) -> Onboarding | None:
        sql = """
        SELECT
            id,
            application_id,
            employer_name,
            job_title,
            joining_date,
            status,
            contract_signed,
            documents_verified,
            orientation_completed,
            accommodation_arranged,
            transport_arranged,
            notes,
            completed_at,
            created_at,
            updated_at
        FROM dbo.onboarding
        WHERE id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                onboarding_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def update(
        self,
        onboarding_id: str,
        employer_name: str | None = None,
        job_title: str | None = None,
        joining_date=None,
        status: str | None = None,
        contract_signed: bool | None = None,
        documents_verified: bool | None = None,
        orientation_completed: bool | None = None,
        accommodation_arranged: bool | None = None,
        transport_arranged: bool | None = None,
        notes: str | None = None,
        completed_at=None,
    ) -> Onboarding:
        current = self.get(onboarding_id)

        if current is None:
            raise ValueError("Onboarding record not found")

        sql = """
        UPDATE dbo.onboarding
        SET
            employer_name = ?,
            job_title = ?,
            joining_date = ?,
            status = ?,
            contract_signed = ?,
            documents_verified = ?,
            orientation_completed = ?,
            accommodation_arranged = ?,
            transport_arranged = ?,
            notes = ?,
            completed_at = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
        """

        new_status = (
            status
            if status is not None
            else current.status
        )

        if (
            completed_at is None
            and new_status == "Completed"
            and current.status != "Completed"
        ):
            completed_at = __import__(
                "datetime"
            ).datetime.utcnow()

        if (
            completed_at is None
            and current.status == "Completed"
            and new_status != "Completed"
        ):
            completed_at = current.completed_at

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                employer_name
                if employer_name is not None
                else current.employer_name,
                job_title
                if job_title is not None
                else current.job_title,
                joining_date
                if joining_date is not None
                else current.joining_date,
                new_status,
                contract_signed
                if contract_signed is not None
                else current.contract_signed,
                documents_verified
                if documents_verified is not None
                else current.documents_verified,
                orientation_completed
                if orientation_completed is not None
                else current.orientation_completed,
                accommodation_arranged
                if accommodation_arranged is not None
                else current.accommodation_arranged,
                transport_arranged
                if transport_arranged is not None
                else current.transport_arranged,
                notes
                if notes is not None
                else current.notes,
                completed_at,
                onboarding_id,
            )
            connection.commit()

        updated = self.get(onboarding_id)

        if updated is None:
            raise ValueError("Onboarding record not found after update")

        return updated
