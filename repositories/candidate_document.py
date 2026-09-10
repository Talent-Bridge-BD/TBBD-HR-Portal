from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import pyodbc
from azure.identity import DefaultAzureCredential

from models.candidate_document import CandidateDocument


SERVER = "tbbd-sql-sea.database.windows.net"
DATABASE = "tbbd-hr-db"
DRIVER = "ODBC Driver 18 for SQL Server"


class CandidateDocumentRepository(ABC):
    @abstractmethod
    def get_candidate_id(self, user_id: str) -> Optional[str]:
        query = """
            SELECT c.id
            FROM dbo.candidates AS c
            WHERE c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, user_id)
            row = cursor.fetchone()

        if row is None:
            return None

        return str(row.id)

    def list_documents(self, user_id: str) -> List[CandidateDocument]:
        raise NotImplementedError

    @abstractmethod
    def get_document(
        self, user_id: str, document_id: str
    ) -> Optional[CandidateDocument]:
        raise NotImplementedError

    @abstractmethod
    def create_document(
        self,
        user_id: str,
        document_type: str,
        file_name: str,
        blob_container: str,
        blob_name: str,
        content_type: Optional[str],
        file_size: Optional[int],
    ) -> CandidateDocument:
        raise NotImplementedError

    @abstractmethod
    def delete_document(self, user_id: str, document_id: str) -> bool:
        raise NotImplementedError


class SqlCandidateDocumentRepository(CandidateDocumentRepository):
    def __init__(self) -> None:
        self.credential = DefaultAzureCredential()

    def _connection(self):
        token = self.credential.get_token(
            "https://database.windows.net/.default"
        )

        connection_string = (
            f"Driver={{{DRIVER}}};"
            f"Server={SERVER};"
            f"Database={DATABASE};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        token_bytes = token.token.encode("utf-16-le")
        token_struct = (
            len(token_bytes).to_bytes(4, "little") + token_bytes
        )

        return pyodbc.connect(
            connection_string,
            attrs_before={1256: token_struct},
        )

    @staticmethod
    def _row_to_document(row) -> CandidateDocument:
        return CandidateDocument(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            document_type=row.document_type,
            file_name=row.file_name,
            blob_container=row.blob_container,
            blob_name=row.blob_name,
            content_type=row.content_type,
            file_size=row.file_size,
            status=row.status,
            uploaded_at=row.uploaded_at,
            verified_at=row.verified_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def get_candidate_id(self, user_id: str) -> Optional[str]:
        query = """
            SELECT c.id
            FROM dbo.candidates AS c
            WHERE c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, user_id)
            row = cursor.fetchone()

        if row is None:
            return None

        return str(row.id)

    def list_documents(self, user_id: str) -> List[CandidateDocument]:
        query = """
            SELECT
                d.id,
                d.candidate_id,
                d.document_type,
                d.file_name,
                d.blob_container,
                d.blob_name,
                d.content_type,
                d.file_size,
                d.status,
                d.uploaded_at,
                d.verified_at,
                d.created_at,
                d.updated_at
            FROM dbo.documents AS d
            INNER JOIN dbo.candidates AS c
                ON c.id = d.candidate_id
            WHERE c.entra_object_id = ?
            ORDER BY d.uploaded_at DESC;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, user_id)
            rows = cursor.fetchall()

        return [self._row_to_document(row) for row in rows]

    def get_document(
        self, user_id: str, document_id: str
    ) -> Optional[CandidateDocument]:
        query = """
            SELECT
                d.id,
                d.candidate_id,
                d.document_type,
                d.file_name,
                d.blob_container,
                d.blob_name,
                d.content_type,
                d.file_size,
                d.status,
                d.uploaded_at,
                d.verified_at,
                d.created_at,
                d.updated_at
            FROM dbo.documents AS d
            INNER JOIN dbo.candidates AS c
                ON c.id = d.candidate_id
            WHERE c.entra_object_id = ?
              AND d.id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, user_id, document_id)
            row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_document(row)

    def create_document(
        self,
        user_id: str,
        document_type: str,
        file_name: str,
        blob_container: str,
        blob_name: str,
        content_type: Optional[str],
        file_size: Optional[int],
    ) -> CandidateDocument:
        document_id = uuid4()
        now = datetime.utcnow()

        query = """
            INSERT INTO dbo.documents (
                id,
                candidate_id,
                application_id,
                document_type,
                file_name,
                blob_container,
                blob_name,
                content_type,
                file_size,
                status,
                uploaded_at,
                verified_at,
                created_at,
                updated_at
            )
            OUTPUT
                inserted.id,
                inserted.candidate_id,
                inserted.document_type,
                inserted.file_name,
                inserted.blob_container,
                inserted.blob_name,
                inserted.content_type,
                inserted.file_size,
                inserted.status,
                inserted.uploaded_at,
                inserted.verified_at,
                inserted.created_at,
                inserted.updated_at
            SELECT
                ?,
                c.id,
                NULL,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                N'submitted',
                ?,
                NULL,
                ?,
                ?
            FROM dbo.candidates AS c
            WHERE c.entra_object_id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                query,
                str(document_id),
                document_type,
                file_name,
                blob_container,
                blob_name,
                content_type,
                file_size,
                now,
                now,
                now,
                user_id,
            )

            row = cursor.fetchone()

            if row is None:
                connection.rollback()
                raise ValueError("Candidate profile was not found")

            connection.commit()

        return self._row_to_document(row)

    def delete_document(self, user_id: str, document_id: str) -> bool:
        query = """
            DELETE d
            FROM dbo.documents AS d
            INNER JOIN dbo.candidates AS c
                ON c.id = d.candidate_id
            WHERE c.entra_object_id = ?
              AND d.id = ?;
        """

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, user_id, document_id)
            deleted = cursor.rowcount > 0
            connection.commit()

        return deleted
