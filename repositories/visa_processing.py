import struct
from abc import ABC, abstractmethod

from azure.identity import DefaultAzureCredential

from models.visa_processing import VisaProcessing


class VisaProcessingRepository(ABC):

    @abstractmethod
    def list_by_application(
        self,
        application_id: str,
    ) -> list[VisaProcessing]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        application_id: str,
        test_type: str | None = None,
        scheduled_at=None,
        location: str | None = None,
        assessor_name: str | None = None,
    ) -> VisaProcessing:
        raise NotImplementedError

    def get(
        self,
        visa_processing_id: str,
    ) -> VisaProcessing | None:
        raise NotImplementedError

    @abstractmethod
    def update_assessment(
        self,
        visa_processing_id: str,
        technical_knowledge_score: int,
        trade_skills_score: int,
        safety_awareness_score: int,
        tool_handling_score: int,
        communication_score: int,
        problem_solving_score: int,
        teamwork_score: int,
        total_score: int,
        result: str,
        status: str,
        assessment_notes: str | None = None,
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
    def _map_row(row) -> VisaProcessing:
        return VisaProcessing(
            id=str(row.id),
            application_id=str(row.application_id),
            test_type=row.test_type,
            scheduled_at=row.scheduled_at,
            location=row.location,
            assessor_name=row.assessor_name,
            technical_knowledge_score=row.technical_knowledge_score,
            trade_skills_score=row.trade_skills_score,
            safety_awareness_score=row.safety_awareness_score,
            tool_handling_score=row.tool_handling_score,
            communication_score=row.communication_score,
            problem_solving_score=row.problem_solving_score,
            teamwork_score=row.teamwork_score,
            total_score=row.total_score,
            result=row.result,
            status=row.status,
            assessment_notes=row.assessment_notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_by_application(
        self,
        application_id: str,
    ) -> list[VisaProcessing]:

        sql = """
        SELECT
            id,
            application_id,
            test_type,
            scheduled_at,
            location,
            assessor_name,
            technical_knowledge_score,
            trade_skills_score,
            safety_awareness_score,
            tool_handling_score,
            communication_score,
            problem_solving_score,
            teamwork_score,
            total_score,
            result,
            status,
            assessment_notes,
            created_at,
            updated_at
        FROM dbo.visa_processings
        WHERE application_id = ?
        ORDER BY scheduled_at DESC, created_at DESC;
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
        test_type: str | None = None,
        scheduled_at=None,
        location: str | None = None,
        assessor_name: str | None = None,
    ) -> VisaProcessing:
        sql = """
        INSERT INTO dbo.visa_processings (
            application_id,
            test_type,
            scheduled_at,
            location,
            assessor_name
        )
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.test_type,
            INSERTED.scheduled_at,
            INSERTED.location,
            INSERTED.assessor_name,
            INSERTED.technical_knowledge_score,
            INSERTED.trade_skills_score,
            INSERTED.safety_awareness_score,
            INSERTED.tool_handling_score,
            INSERTED.communication_score,
            INSERTED.problem_solving_score,
            INSERTED.teamwork_score,
            INSERTED.total_score,
            INSERTED.result,
            INSERTED.status,
            INSERTED.assessment_notes,
            INSERTED.created_at,
            INSERTED.updated_at
        VALUES (?, ?, ?, ?, ?);
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                application_id,
                test_type,
                scheduled_at,
                location,
                assessor_name,
            )
            row = cursor.fetchone()
            connection.commit()

        return self._map_row(row)

    def get(
        self,
        visa_processing_id: str,
    ) -> VisaProcessing | None:

        sql = """
        SELECT
            id,
            application_id,
            test_type,
            scheduled_at,
            location,
            assessor_name,
            technical_knowledge_score,
            trade_skills_score,
            safety_awareness_score,
            tool_handling_score,
            communication_score,
            problem_solving_score,
            teamwork_score,
            total_score,
            result,
            status,
            assessment_notes,
            created_at,
            updated_at
        FROM dbo.visa_processings
        WHERE id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                visa_processing_id,
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def update_assessment(
        self,
        visa_processing_id: str,
        technical_knowledge_score: int,
        trade_skills_score: int,
        safety_awareness_score: int,
        tool_handling_score: int,
        communication_score: int,
        problem_solving_score: int,
        teamwork_score: int,
        result: str,
        status: str,
        assessment_notes: str | None = None,
    ) -> VisaProcessing:

        sql = """
        UPDATE dbo.visa_processings
        SET
            technical_knowledge_score = ?,
            trade_skills_score = ?,
            safety_awareness_score = ?,
            tool_handling_score = ?,
            communication_score = ?,
            problem_solving_score = ?,
            teamwork_score = ?,
            total_score = ?,
            result = ?,
            status = ?,
            assessment_notes = ?,
            updated_at = SYSUTCDATETIME()
        OUTPUT
            INSERTED.id,
            INSERTED.application_id,
            INSERTED.test_type,
            INSERTED.scheduled_at,
            INSERTED.location,
            INSERTED.assessor_name,
            INSERTED.technical_knowledge_score,
            INSERTED.trade_skills_score,
            INSERTED.safety_awareness_score,
            INSERTED.tool_handling_score,
            INSERTED.communication_score,
            INSERTED.problem_solving_score,
            INSERTED.teamwork_score,
            INSERTED.total_score,
            INSERTED.result,
            INSERTED.status,
            INSERTED.assessment_notes,
            INSERTED.created_at,
            INSERTED.updated_at
        WHERE id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                sql,
                technical_knowledge_score,
                trade_skills_score,
                safety_awareness_score,
                tool_handling_score,
                communication_score,
                problem_solving_score,
                teamwork_score,
                total_score,
                result,
                status,
                assessment_notes,
                visa_processing_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError("Trade test not found")

            connection.commit()

        return self._map_row(row)

