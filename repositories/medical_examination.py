import struct

from abc import ABC, abstractmethod

from azure.identity import DefaultAzureCredential

from models.medical_examination import MedicalExamination


class MedicalExaminationRepository(ABC):

    @abstractmethod
    def list_by_application(
        self,
        application_id: str,
    ) -> list[MedicalExamination]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        application_id: str,
        medical_center: str | None = None,
        examination_date=None,
        doctor_name: str | None = None,
        medical_type: str | None = None,
    ) -> MedicalExamination:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        medical_examination_id: str,
    ) -> MedicalExamination | None:
        raise NotImplementedError

    @abstractmethod
    def update_assessment(
        self,
        medical_examination_id: str,
        medical_center: str | None,
        examination_date,
        doctor_name: str | None,
        medical_type: str | None,
        status: str,
        result: str,
        report_notes: str | None = None,
        completed_at=None,
    ) -> MedicalExamination:
        raise NotImplementedError


class SqlMedicalExaminationRepository(MedicalExaminationRepository):

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
    def _map_row(row) -> MedicalExamination:
        return MedicalExamination(
            id=str(row.id),
            application_id=str(row.application_id),
            medical_center=row.medical_center,
            examination_date=row.examination_date,
            doctor_name=row.doctor_name,
            medical_type=row.medical_type,
            status=row.status,
            result=row.result,
            report_notes=row.report_notes,
            completed_at=row.completed_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_by_application(
        self,
        application_id: str,
    ) -> list[MedicalExamination]:

        sql = """
        SELECT
            id,
            application_id,
            medical_center,
            examination_date,
            doctor_name,
            medical_type,
            status,
            result,
            report_notes,
            completed_at,
            created_at,
            updated_at
        FROM dbo.medical_examinations
        WHERE application_id = ?
        ORDER BY examination_date DESC, created_at DESC;
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
        medical_center: str | None = None,
        examination_date=None,
        doctor_name: str | None = None,
        medical_type: str | None = None,
    ) -> MedicalExamination:

        sql = """
        INSERT INTO dbo.medical_examinations (
            application_id,
            medical_center,
            examination_date,
            doctor_name,
            medical_type
        )
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.medical_center,
            INSERTED.examination_date,
            INSERTED.doctor_name,
            INSERTED.medical_type,
            INSERTED.status,
            INSERTED.result,
            INSERTED.report_notes,
            INSERTED.completed_at,
            INSERTED.created_at,
            INSERTED.updated_at
        VALUES (?, ?, ?, ?, ?);
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                application_id,
                medical_center,
                examination_date,
                doctor_name,
                medical_type,
            )

            row = cursor.fetchone()
            connection.commit()

        return self._map_row(row)

    def get(
        self,
        medical_examination_id: str,
    ) -> MedicalExamination | None:

        sql = """
        SELECT
            id,
            application_id,
            medical_center,
            examination_date,
            doctor_name,
            medical_type,
            status,
            result,
            report_notes,
            completed_at,
            created_at,
            updated_at
        FROM dbo.medical_examinations
        WHERE id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                medical_examination_id,
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def update_assessment(
        self,
        medical_examination_id: str,
        medical_center: str | None,
        examination_date,
        doctor_name: str | None,
        medical_type: str | None,
        status: str,
        result: str,
        report_notes: str | None = None,
        completed_at=None,
    ) -> MedicalExamination:

        sql = """
        UPDATE dbo.medical_examinations
        SET
            medical_center = ?,
            examination_date = ?,
            doctor_name = ?,
            medical_type = ?,
            status = ?,
            result = ?,
            report_notes = ?,
            completed_at = ?,
            updated_at = SYSUTCDATETIME()
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.medical_center,
            INSERTED.examination_date,
            INSERTED.doctor_name,
            INSERTED.medical_type,
            INSERTED.status,
            INSERTED.result,
            INSERTED.report_notes,
            INSERTED.completed_at,
            INSERTED.created_at,
            INSERTED.updated_at
        WHERE id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                sql,
                medical_center,
                examination_date,
                doctor_name,
                medical_type,
                status,
                result,
                report_notes,
                completed_at,
                medical_examination_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError("Medical examination not found")

            connection.commit()

        return self._map_row(row)
