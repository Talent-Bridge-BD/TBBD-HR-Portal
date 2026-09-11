from __future__ import annotations

import os
import struct
from abc import ABC, abstractmethod
from typing import Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.candidate_document import CandidateDocument


class CandidateDocumentRepository(ABC):

    @abstractmethod
    def list_documents(self, candidate_id: str) -> list[CandidateDocument]:
        raise NotImplementedError

    @abstractmethod
    def get_document(
        self,
        candidate_id: str,
        document_id: str,
    ) -> Optional[CandidateDocument]:
        raise NotImplementedError

    @abstractmethod
    def create_document(
        self,
        candidate_id: str,
        document_type: str,
        file_name: str,
        blob_container: str,
        blob_name: str,
        content_type: Optional[str],
        file_size: Optional[int],
    ) -> CandidateDocument:
        raise NotImplementedError

    @abstractmethod
    def replace_document(
        self,
        candidate_id: str,
        document_type: str,
        file_name: str,
        blob_container: str,
        blob_name: str,
        content_type: Optional[str],
        file_size: Optional[int],
    ) -> tuple[CandidateDocument, Optional[CandidateDocument]]:
        raise NotImplementedError

    @abstractmethod
    def delete_document(
        self,
        candidate_id: str,
        document_id: str,
    ) -> Optional[CandidateDocument]:
        raise NotImplementedError


class SqlCandidateDocumentRepository(CandidateDocumentRepository):
    """
    Azure SQL repository for candidate document metadata.

    Profile-level passport and resume documents are unique per candidate.
    The file itself is stored in private Azure Blob Storage.
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
        ) + token_bytes

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
    def _map_row(row) -> CandidateDocument:
        return CandidateDocument(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            document_type=str(row.document_type),
            file_name=str(row.file_name),
            blob_container=str(row.blob_container),
            blob_name=str(row.blob_name),
            content_type=row.content_type,
            file_size=row.file_size,
            status=str(row.status),
            uploaded_at=(
                row.uploaded_at.isoformat()
                if row.uploaded_at is not None
                else None
            ),
        )

    @staticmethod
    def _select_columns() -> str:
        return """
            id,
            candidate_id,
            document_type,
            file_name,
            blob_container,
            blob_name,
            content_type,
            file_size,
            status,
            uploaded_at
        """

    def list_documents(
        self,
        candidate_id: str,
    ) -> list[CandidateDocument]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                SELECT
                    {self._select_columns()}
                FROM dbo.documents
                WHERE candidate_id = ?
                  AND application_id IS NULL
                ORDER BY created_at DESC
                """,
                candidate_id,
            )

            rows = cursor.fetchall()

        return [self._map_row(row) for row in rows]

    def get_document(
        self,
        candidate_id: str,
        document_id: str,
    ) -> Optional[CandidateDocument]:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                SELECT
                    {self._select_columns()}
                FROM dbo.documents
                WHERE id = ?
                  AND candidate_id = ?
                  AND application_id IS NULL
                """,
                document_id,
                candidate_id,
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def create_document(
        self,
        candidate_id: str,
        document_type: str,
        file_name: str,
        blob_container: str,
        blob_name: str,
        content_type: Optional[str],
        file_size: Optional[int],
    ) -> CandidateDocument:
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                f"""
                INSERT INTO dbo.documents (
                    candidate_id,
                    application_id,
                    document_type,
                    file_name,
                    blob_container,
                    blob_name,
                    content_type,
                    file_size,
                    status
                )
                OUTPUT
                    INSERTED.id,
                    INSERTED.candidate_id,
                    INSERTED.document_type,
                    INSERTED.file_name,
                    INSERTED.blob_container,
                    INSERTED.blob_name,
                    INSERTED.content_type,
                    INSERTED.file_size,
                    INSERTED.status,
                    INSERTED.uploaded_at
                VALUES (
                    ?,
                    NULL,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    N'uploaded'
                )
                """,
                candidate_id,
                document_type,
                file_name,
                blob_container,
                blob_name,
                content_type,
                file_size,
            )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError(
                    "Candidate document metadata could not be created"
                )

            connection.commit()

        return self._map_row(row)

    def replace_document(
        self,
        candidate_id: str,
        document_type: str,
        file_name: str,
        blob_container: str,
        blob_name: str,
        content_type: Optional[str],
        file_size: Optional[int],
    ) -> tuple[CandidateDocument, Optional[CandidateDocument]]:
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                f"""
                SELECT
                    {self._select_columns()}
                FROM dbo.documents WITH (UPDLOCK, HOLDLOCK)
                WHERE candidate_id = ?
                  AND application_id IS NULL
                  AND document_type = ?
                """,
                candidate_id,
                document_type,
            )

            old_row = cursor.fetchone()

            cursor.execute(
                """
                IF EXISTS (
                    SELECT 1
                    FROM dbo.documents
                    WHERE candidate_id = ?
                      AND application_id IS NULL
                      AND document_type = ?
                )
                BEGIN
                    DELETE FROM dbo.documents
                    WHERE candidate_id = ?
                      AND application_id IS NULL
                      AND document_type = ?
                END
                """,
                candidate_id,
                document_type,
                candidate_id,
                document_type,
            )

            cursor.execute(
                f"""
                INSERT INTO dbo.documents (
                    candidate_id,
                    application_id,
                    document_type,
                    file_name,
                    blob_container,
                    blob_name,
                    content_type,
                    file_size,
                    status
                )
                OUTPUT
                    INSERTED.id,
                    INSERTED.candidate_id,
                    INSERTED.document_type,
                    INSERTED.file_name,
                    INSERTED.blob_container,
                    INSERTED.blob_name,
                    INSERTED.content_type,
                    INSERTED.file_size,
                    INSERTED.status,
                    INSERTED.uploaded_at
                VALUES (
                    ?,
                    NULL,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    N'uploaded'
                )
                """,
                candidate_id,
                document_type,
                file_name,
                blob_container,
                blob_name,
                content_type,
                file_size,
            )

            new_row = cursor.fetchone()

            if new_row is None:
                connection.rollback()
                raise RuntimeError(
                    "Replacement document metadata could not be created"
                )

            connection.commit()

        new_document = self._map_row(new_row)

        old_document = (
            self._map_row(old_row)
            if old_row is not None
            else None
        )

        return new_document, old_document

    def delete_document(
        self,
        candidate_id: str,
        document_id: str,
    ) -> Optional[CandidateDocument]:
        document = self.get_document(
            candidate_id,
            document_id,
        )

        if document is None:
            return None

        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE FROM dbo.documents
                WHERE id = ?
                  AND candidate_id = ?
                  AND application_id IS NULL
                """,
                document_id,
                candidate_id,
            )

            connection.commit()

        return document
