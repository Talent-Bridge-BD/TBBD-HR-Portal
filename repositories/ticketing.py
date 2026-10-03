import struct
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from azure.identity import DefaultAzureCredential

from models.ticketing import Ticketing


class TicketingRepository(ABC):

    @abstractmethod
    def list_by_application(
        self,
        application_id: str,
    ) -> list[Ticketing]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        application_id: str,
        airline_name: Optional[str] = None,
        flight_number: Optional[str] = None,
        booking_reference: Optional[str] = None,
        ticket_number: Optional[str] = None,
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        departure_datetime: Optional[datetime] = None,
        arrival_datetime: Optional[datetime] = None,
    ) -> Ticketing:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        ticketing_id: str,
    ) -> Ticketing | None:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        ticketing_id: str,
        airline_name: Optional[str],
        flight_number: Optional[str],
        booking_reference: Optional[str],
        ticket_number: Optional[str],
        departure_airport: Optional[str],
        arrival_airport: Optional[str],
        departure_datetime: Optional[datetime],
        arrival_datetime: Optional[datetime],
        status: str,
        ticket_document_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Ticketing:
        raise NotImplementedError


class SqlTicketingRepository(TicketingRepository):

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
    def _map_row(row) -> Ticketing:
        return Ticketing(
            id=str(row.id),
            application_id=str(row.application_id),
            airline_name=row.airline_name,
            flight_number=row.flight_number,
            booking_reference=row.booking_reference,
            ticket_number=row.ticket_number,
            departure_airport=row.departure_airport,
            arrival_airport=row.arrival_airport,
            departure_datetime=row.departure_datetime,
            arrival_datetime=row.arrival_datetime,
            status=row.status,
            ticket_document_reference=row.ticket_document_reference,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_by_application(
        self,
        application_id: str,
    ) -> list[Ticketing]:

        sql = """
        SELECT
            id,
            application_id,
            airline_name,
            flight_number,
            booking_reference,
            ticket_number,
            departure_airport,
            arrival_airport,
            departure_datetime,
            arrival_datetime,
            status,
            ticket_document_reference,
            notes,
            created_at,
            updated_at
        FROM dbo.ticketing
        WHERE application_id = ?
        ORDER BY departure_datetime DESC, created_at DESC;
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
        airline_name: Optional[str] = None,
        flight_number: Optional[str] = None,
        booking_reference: Optional[str] = None,
        ticket_number: Optional[str] = None,
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        departure_datetime: Optional[datetime] = None,
        arrival_datetime: Optional[datetime] = None,
    ) -> Ticketing:

        sql = """
        INSERT INTO dbo.ticketing (
            application_id,
            airline_name,
            flight_number,
            booking_reference,
            ticket_number,
            departure_airport,
            arrival_airport,
            departure_datetime,
            arrival_datetime
        )
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.airline_name,
            INSERTED.flight_number,
            INSERTED.booking_reference,
            INSERTED.ticket_number,
            INSERTED.departure_airport,
            INSERTED.arrival_airport,
            INSERTED.departure_datetime,
            INSERTED.arrival_datetime,
            INSERTED.status,
            INSERTED.ticket_document_reference,
            INSERTED.notes,
            INSERTED.created_at,
            INSERTED.updated_at
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                airline_name,
                flight_number,
                booking_reference,
                ticket_number,
                departure_airport,
                arrival_airport,
                departure_datetime,
                arrival_datetime,
            )
            row = cursor.fetchone()
            connection.commit()

        return self._map_row(row)

    def get(
        self,
        ticketing_id: str,
    ) -> Ticketing | None:

        sql = """
        SELECT
            id,
            application_id,
            airline_name,
            flight_number,
            booking_reference,
            ticket_number,
            departure_airport,
            arrival_airport,
            departure_datetime,
            arrival_datetime,
            status,
            ticket_document_reference,
            notes,
            created_at,
            updated_at
        FROM dbo.ticketing
        WHERE id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                ticketing_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def update(
        self,
        ticketing_id: str,
        airline_name: Optional[str],
        flight_number: Optional[str],
        booking_reference: Optional[str],
        ticket_number: Optional[str],
        departure_airport: Optional[str],
        arrival_airport: Optional[str],
        departure_datetime: Optional[datetime],
        arrival_datetime: Optional[datetime],
        status: str,
        ticket_document_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Ticketing:

        sql = """
        UPDATE dbo.ticketing
        SET
            airline_name = ?,
            flight_number = ?,
            booking_reference = ?,
            ticket_number = ?,
            departure_airport = ?,
            arrival_airport = ?,
            departure_datetime = ?,
            arrival_datetime = ?,
            status = ?,
            ticket_document_reference = ?,
            notes = ?,
            updated_at = SYSUTCDATETIME()
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.airline_name,
            INSERTED.flight_number,
            INSERTED.booking_reference,
            INSERTED.ticket_number,
            INSERTED.departure_airport,
            INSERTED.arrival_airport,
            INSERTED.departure_datetime,
            INSERTED.arrival_datetime,
            INSERTED.status,
            INSERTED.ticket_document_reference,
            INSERTED.notes,
            INSERTED.created_at,
            INSERTED.updated_at
        WHERE id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                airline_name,
                flight_number,
                booking_reference,
                ticket_number,
                departure_airport,
                arrival_airport,
                departure_datetime,
                arrival_datetime,
                status,
                ticket_document_reference,
                notes,
                ticketing_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError("Ticketing record not found")

            connection.commit()

        return self._map_row(row)
